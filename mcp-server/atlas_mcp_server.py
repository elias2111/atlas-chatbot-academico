#!/usr/bin/env python3
"""
ATLAS · Servidor MCP (Model Context Protocol)
=============================================
Expone la base de datos académica de ATLAS (PostgreSQL) como herramientas MCP que un
agente de IA puede descubrir y llamar: estado académico, notas del semestre, tareas,
prerrequisitos y noticias del día.

Transportes:
  • stdio  (por defecto)        -> Claude Desktop, MCP Inspector, cualquier cliente MCP
  • HTTP   (--http PUERTO)      -> POST /mcp con JSON-RPC 2.0 (probar con curl o Postman)

Fuentes de datos (se elige sola según las variables de entorno):
  • SUPABASE_URL + SUPABASE_KEY -> API REST de Supabase (PostgREST), sin dependencias
  • DATABASE_URL                -> PostgreSQL directo con el cliente `psql`

Solo usa la biblioteca estándar de Python 3.9+.

  python mcp-server/atlas_mcp_server.py                 # stdio
  python mcp-server/atlas_mcp_server.py --http 8765     # HTTP en http://localhost:8765/mcp
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SERVER_INFO = {"name": "atlas-academico", "version": "1.0.0"}
PROTOCOL = "2025-03-26"
CATEGORIAS_TAREA = ["", "vencida", "incompleta", "por hacer", "entregada"]
CATEGORIAS_NOTICIA = ["", "Educación", "Tecnología", "Ingeniería de sistemas"]

TOOLS = [
    {"name": "consultar_estado_academico",
     "description": "Estado académico completo del estudiante: programa, periodo, estado de matrícula, créditos aprobados y en curso, "
                    "porcentaje de avance, promedio (PGA), materias en curso y pendientes con los prerrequisitos que le faltan.",
     "inputSchema": {"type": "object", "properties": {"codigo": {"type": "string", "description": "Código del estudiante, p. ej. 20221045"}},
                     "required": ["codigo"]}},
    {"name": "consultar_notas_semestre",
     "description": "Notas del semestre actual por materia en escala 0,0–5,0: evaluaciones (corte, peso, nota), nota actual, acumulado, "
                    "nota necesaria para aprobar con 3,0 y estado (APROBANDO, EN RIESGO, APROBADA ASEGURADA, PERDIDA, APROBADA, REPROBADA).",
     "inputSchema": {"type": "object", "properties": {"codigo": {"type": "string"}}, "required": ["codigo"]}},
    {"name": "consultar_tareas",
     "description": "Tareas del estudiante con fecha de entrega, días restantes, estado y avance. Filtro opcional por categoría.",
     "inputSchema": {"type": "object", "properties": {"codigo": {"type": "string"},
                                                       "categoria": {"type": "string", "enum": CATEGORIAS_TAREA, "description": "vacío = todas"}},
                     "required": ["codigo"]}},
    {"name": "consultar_prerrequisitos",
     "description": "Prerrequisitos de una asignatura del plan de Ingeniería de Sistemas (151 créditos) y las asignaturas que desbloquea.",
     "inputSchema": {"type": "object", "properties": {"asignatura": {"type": "string", "description": "Nombre o código, p. ej. 'Dinámica de sistemas' o DSIS"}},
                     "required": ["asignatura"]}},
    {"name": "noticias_del_dia",
     "description": "Noticias de las últimas 48 horas sobre educación, tecnología e ingeniería de sistemas, con fuente, fecha y enlace.",
     "inputSchema": {"type": "object", "properties": {"categoria": {"type": "string", "enum": CATEGORIAS_NOTICIA, "description": "vacío = todas"}}}},
]


class ErrorHerramienta(Exception):
    pass


# ---------------------------------------------------------------- guardrails de parámetros
def validar(nombre: str, args: dict) -> dict:
    args = dict(args or {})
    if "codigo" in [p for t in TOOLS if t["name"] == nombre for p in t["inputSchema"].get("required", [])]:
        if not re.fullmatch(r"[0-9A-Za-z-]{1,20}", str(args.get("codigo", ""))):
            raise ErrorHerramienta("El parámetro 'codigo' debe ser alfanumérico (máx. 20 caracteres).")
    if nombre == "consultar_tareas" and args.get("categoria", "") not in CATEGORIAS_TAREA:
        raise ErrorHerramienta(f"categoria inválida. Opciones: {CATEGORIAS_TAREA[1:]}")
    if nombre == "noticias_del_dia" and args.get("categoria", "") not in CATEGORIAS_NOTICIA:
        raise ErrorHerramienta(f"categoria inválida. Opciones: {CATEGORIAS_NOTICIA[1:]}")
    if nombre == "consultar_prerrequisitos":
        a = str(args.get("asignatura", "")).strip()
        if not a or len(a) > 80:
            raise ErrorHerramienta("Indica el nombre o código de la asignatura (máx. 80 caracteres).")
        args["asignatura"] = a
    return args


# ---------------------------------------------------------------- acceso a datos
class Rest:
    """Supabase / PostgREST: llama las funciones SQL por /rest/v1/rpc/<funcion>."""
    def __init__(self, url: str, key: str):
        self.url, self.key = url.rstrip("/"), key

    def _req(self, path: str, body: dict | None = None):
        req = urllib.request.Request(self.url + "/rest/v1/" + path, method="POST" if body is not None else "GET",
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"apikey": self.key, "Authorization": f"Bearer {self.key}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read() or b"null")

    def rpc(self, fn: str, **params):
        return self._req(f"rpc/{fn}", params)

    def noticias(self, categoria: str):
        q = "v_noticias_hoy?select=titulo,fuente,categoria,fecha,url&limit=10"
        if categoria:
            q += "&categoria=eq." + urllib.request.quote(categoria)
        return self._req(q)


class Psql:
    """PostgreSQL directo con `psql`; los parámetros viajan como variables (:'p1'), nunca concatenados."""
    def __init__(self, dsn: str):
        self.dsn = dsn

    def _q(self, sql: str, *params: str):
        cmd = ["psql", self.dsn, "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1"]
        for i, p in enumerate(params, 1):
            cmd += ["-v", f"p{i}={p}"]
        r = subprocess.run(cmd, input=sql, capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            raise ErrorHerramienta("Error de base de datos: " + r.stderr.strip()[:200])
        out = r.stdout.strip()
        return json.loads(out) if out else None

    def rpc(self, fn: str, **params):
        vals = list(params.values())
        args = ", ".join(f":'p{i}'" for i in range(1, len(vals) + 1))
        return self._q(f"SELECT {fn}({args});", *[("" if v is None else str(v)) for v in vals])

    def noticias(self, categoria: str):
        return self._q("SELECT COALESCE(json_agg(n), '[]') FROM (SELECT titulo, fuente, categoria, fecha, url FROM v_noticias_hoy "
                       "WHERE (:'p1' = '' OR categoria = :'p1') LIMIT 10) n;", categoria)


def backend():
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY"):
        return Rest(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    if os.environ.get("DATABASE_URL"):
        return Psql(os.environ["DATABASE_URL"])
    raise SystemExit("Configura SUPABASE_URL y SUPABASE_KEY, o DATABASE_URL.")


DB = None


def ejecutar(nombre: str, args: dict):
    args = validar(nombre, args)
    if nombre == "consultar_estado_academico":
        r = DB.rpc("fn_contexto_estudiante", p_codigo=args["codigo"])
        if not r or not r.get("estudiante"):
            raise ErrorHerramienta(f"No existe un estudiante con código {args['codigo']}.")
        return r
    if nombre == "consultar_notas_semestre":
        return DB.rpc("fn_notas_semestre", p_codigo=args["codigo"])
    if nombre == "consultar_tareas":
        return DB.rpc("fn_tareas", p_codigo=args["codigo"], p_categoria=args.get("categoria") or None)
    if nombre == "consultar_prerrequisitos":
        r = DB.rpc("fn_prerrequisitos", p_asignatura=args["asignatura"])
        if not r:
            raise ErrorHerramienta(f"No encontré la asignatura '{args['asignatura']}' en el plan.")
        return r
    if nombre == "noticias_del_dia":
        return DB.noticias(args.get("categoria", ""))
    raise ErrorHerramienta(f"Herramienta desconocida: {nombre}")


# ---------------------------------------------------------------- JSON-RPC / MCP
def manejar(msg: dict) -> dict | None:
    mid, metodo = msg.get("id"), msg.get("method")
    ok = lambda res: {"jsonrpc": "2.0", "id": mid, "result": res}
    if metodo == "initialize":
        version = (msg.get("params") or {}).get("protocolVersion") or PROTOCOL
        return ok({"protocolVersion": version, "capabilities": {"tools": {"listChanged": False}}, "serverInfo": SERVER_INFO,
                   "instructions": "Herramientas de solo lectura sobre la base de datos académica de ATLAS (Ingeniería de Sistemas, UNAB)."})
    if metodo in ("notifications/initialized", "notifications/cancelled"):
        return None
    if metodo == "ping":
        return ok({})
    if metodo == "tools/list":
        return ok({"tools": TOOLS})
    if metodo == "tools/call":
        p = msg.get("params") or {}
        try:
            data = ejecutar(p.get("name"), p.get("arguments") or {})
            return ok({"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, default=str)}], "isError": False})
        except ErrorHerramienta as e:
            return ok({"content": [{"type": "text", "text": str(e)}], "isError": True})
        except Exception as e:  # error de red / base de datos
            return ok({"content": [{"type": "text", "text": f"Error interno: {e}"}], "isError": True})
    if mid is None:
        return None
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Método no soportado: {metodo}"}}


def stdio():
    for linea in sys.stdin:
        linea = linea.strip()
        if not linea:
            continue
        try:
            msg = json.loads(linea)
        except json.JSONDecodeError:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON inválido"}}), flush=True)
            continue
        resp = [manejar(m) for m in msg] if isinstance(msg, list) else manejar(msg)
        if resp:
            print(json.dumps(resp, ensure_ascii=False), flush=True)


class Http(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Mcp-Session-Id")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        if self.path.startswith("/health"):
            return self._send(200, {"ok": True, "server": SERVER_INFO, "tools": [t["name"] for t in TOOLS]})
        self._send(404, {"error": "usa POST /mcp"})

    def do_POST(self):
        if not self.path.startswith("/mcp"):
            return self._send(404, {"error": "usa POST /mcp"})
        try:
            msg = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON inválido"}})
        resp = [manejar(m) for m in msg] if isinstance(msg, list) else manejar(msg)
        self._send(200 if resp else 202, resp or {})

    def log_message(self, fmt, *a):
        sys.stderr.write("[mcp-http] " + fmt % a + "\n")


def main():
    global DB
    ap = argparse.ArgumentParser(description="Servidor MCP de ATLAS")
    ap.add_argument("--http", type=int, help="puerto para el transporte HTTP (POST /mcp)")
    a = ap.parse_args()
    DB = backend()
    if a.http:
        print(f"ATLAS MCP escuchando en http://localhost:{a.http}/mcp", file=sys.stderr)
        ThreadingHTTPServer(("0.0.0.0", a.http), Http).serve_forever()
    else:
        stdio()


if __name__ == "__main__":
    main()
