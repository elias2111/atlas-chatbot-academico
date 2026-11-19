#!/usr/bin/env python3
"""Cliente de prueba: arranca el servidor MCP por stdio, hace el handshake, lista las
herramientas y llama cada una. Imprime la conversación JSON-RPC completa (evidencia)."""
import json, subprocess, sys, os
from pathlib import Path

srv = subprocess.Popen([sys.executable, str(Path(__file__).with_name("atlas_mcp_server.py"))], stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE, text=True, env=os.environ.copy())
n = 0
def rpc(method, params=None, notify=False):
    global n
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None: msg["params"] = params
    if not notify: n += 1; msg["id"] = n
    print("\n→ " + json.dumps(msg, ensure_ascii=False))
    srv.stdin.write(json.dumps(msg) + "\n"); srv.stdin.flush()
    if notify: return None
    resp = json.loads(srv.stdout.readline())
    txt = json.dumps(resp, ensure_ascii=False)
    print("← " + (txt if len(txt) < 900 else txt[:900] + " …"))
    return resp

rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "probar_mcp", "version": "1"}})
rpc("notifications/initialized", notify=True)
tools = rpc("tools/list")["result"]["tools"]
print(f"\n# {len(tools)} herramientas: " + ", ".join(t["name"] for t in tools))
casos = [("consultar_estado_academico", {"codigo": "20221045"}),
         ("consultar_notas_semestre", {"codigo": "20221045"}),
         ("consultar_tareas", {"codigo": "20221045", "categoria": "vencida"}),
         ("consultar_prerrequisitos", {"asignatura": "Dinámica de sistemas"}),
         ("noticias_del_dia", {"categoria": "Educación"}),
         ("consultar_tareas", {"codigo": "20221045'; DROP TABLE tarea;--"}),   # guardrail: debe rechazarse
         ("consultar_estado_academico", {"codigo": "99999999"})]               # estudiante inexistente
ok = 0
for nombre, args in casos:
    r = rpc("tools/call", {"name": nombre, "arguments": args})["result"]
    esperado_error = "DROP" in json.dumps(args) or args.get("codigo") == "99999999"
    ok += (r["isError"] == esperado_error)
print(f"\n# Resultado: {ok}/{len(casos)} casos con el comportamiento esperado")
srv.stdin.close(); srv.wait(timeout=5)
