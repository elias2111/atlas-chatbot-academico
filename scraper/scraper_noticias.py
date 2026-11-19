#!/usr/bin/env python3
"""
ATLAS · Scraper de noticias del día
-----------------------------------
Recolecta noticias recientes de educación, tecnología e ingeniería de sistemas desde
fuentes RSS públicas, las filtra por fecha (últimas 48 h por defecto), las clasifica por
categoría, elimina duplicados y publica:

  1. data/noticias.json          -> lo consume la app (GitHub Pages, mismo origen)
  2. tabla `noticias` en Supabase -> la consume el agente de n8n y el servidor MCP
     (solo si existen las variables SUPABASE_URL y SUPABASE_KEY)

Solo usa la biblioteca estándar de Python (corre en GitHub Actions sin instalar nada).

Uso:
  python scraper/scraper_noticias.py                 # modo normal
  python scraper/scraper_noticias.py --horas 72      # ventana de tiempo distinta
  python scraper/scraper_noticias.py --fixture f.xml # prueba offline con un RSS local
"""
from __future__ import annotations

import argparse
import email.utils
import hashlib
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "data" / "noticias.json"
UA = "Mozilla/5.0 (compatible; ATLAS-scraper/1.0; +https://github.com/elias2111/atlas-chatbot-academico)"
BOGOTA = timezone(timedelta(hours=-5))


def gnews(consulta: str) -> str:
    """URL de búsqueda RSS de Google Noticias para Colombia, en español."""
    q = urllib.parse.quote(f"{consulta} when:2d")
    return f"https://news.google.com/rss/search?q={q}&hl=es-419&gl=CO&ceid=CO:es-419"


# (categoría, nombre de la fuente, URL del feed)
FUENTES = [
    ("Ingeniería de sistemas", "Google Noticias", gnews('"ingeniería de sistemas" OR "ingeniería de software" OR programadores Colombia')),
    ("Ingeniería de sistemas", "Google Noticias", gnews('ciberseguridad OR "desarrollo de software" OR "ciencia de datos" empleo Colombia')),
    ("Tecnología",             "Google Noticias", gnews('"inteligencia artificial" OR tecnología OR startups Colombia')),
    ("Tecnología",             "Xataka",          "https://www.xataka.com/feedburner.xml"),
    ("Educación",              "Google Noticias", gnews('educación superior OR universidades OR "Ministerio de Educación" Colombia')),
    ("Educación",              "Google Noticias", gnews('ICETEX OR "Saber Pro" OR becas universitarias Colombia')),
]

# Palabras clave para reclasificar o descartar (se compara sin tildes y en minúscula)
CLAVES = {
    "Ingeniería de sistemas": ["ingenieria de sistemas", "software", "programador", "programacion", "desarrollador", "ciberseguridad",
                               "hacker", "datos", "data", "nube", "cloud", "algoritmo", "devops", "backend", "frontend", "base de datos"],
    "Tecnología": ["inteligencia artificial", " ia ", "openai", "chatgpt", "claude", "gemini", "tecnologia", "robot", "chip", "startup",
                   "app", "celular", "smartphone", "apple", "google", "microsoft", "5g", "ciber"],
    "Educación": ["universidad", "educacion", "estudiante", "icetex", "saber pro", "beca", "mineducacion", "colegio", "docente",
                  "matricula", "pregrado", "posgrado", "academic"],
}


def sin_tildes(t: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")


def limpiar(texto: str | None) -> str:
    if not texto:
        return ""
    texto = re.sub(r"<[^>]+>", " ", html.unescape(texto))
    return re.sub(r"\s+", " ", texto).strip()


def fecha_rss(valor: str | None) -> datetime | None:
    if not valor:
        return None
    try:
        d = email.utils.parsedate_to_datetime(valor)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def descargar(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parsear_rss(xml_bytes: bytes, categoria: str, fuente_feed: str) -> list[dict]:
    """Soporta RSS 2.0 y Atom."""
    raiz = ET.fromstring(xml_bytes)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = raiz.findall(".//item") or raiz.findall(".//atom:entry", ns)
    salida = []
    for it in items:
        def txt(tag):
            el = it.find(tag) if not tag.startswith("atom:") else it.find(tag, ns)
            return el.text if el is not None else None
        titulo = limpiar(txt("title") or txt("atom:title"))
        link = txt("link")
        if not link:
            el = it.find("atom:link", ns)
            link = el.get("href") if el is not None else None
        fecha = fecha_rss(txt("pubDate") or txt("atom:updated") or txt("atom:published"))
        fuente_el = it.find("source")
        fuente = limpiar(fuente_el.text) if fuente_el is not None and fuente_el.text else fuente_feed
        # Google Noticias agrega " - Medio" al final del título
        if fuente_feed == "Google Noticias" and " - " in titulo:
            base, medio = titulo.rsplit(" - ", 1)
            if len(medio) < 60:
                titulo, fuente = base.strip(), medio.strip()
        resumen = limpiar(txt("description") or txt("atom:summary"))
        if resumen.startswith(titulo[:40]):
            resumen = ""
        if titulo and link:
            salida.append({"titulo": titulo, "url": link.strip(), "fuente": fuente or fuente_feed, "categoria": categoria,
                           "fecha": fecha.isoformat() if fecha else None, "resumen": resumen[:280]})
    return salida


def clasificar(n: dict) -> str | None:
    """Confirma la categoría por palabras clave. Devuelve None si la noticia no es pertinente."""
    texto = " " + sin_tildes(n["titulo"] + " " + n.get("resumen", "")) + " "
    puntos = {cat: sum(1 for k in claves if k in texto) for cat, claves in CLAVES.items()}
    if puntos.get(n["categoria"], 0) > 0:
        return n["categoria"]
    mejor = max(puntos, key=puntos.get)
    return mejor if puntos[mejor] > 0 else None


def clave_dup(titulo: str) -> str:
    palabras = [w for w in re.findall(r"[a-z0-9]+", sin_tildes(titulo)) if len(w) > 3][:8]
    return hashlib.md5(" ".join(sorted(palabras)).encode()).hexdigest()


def recolectar(horas: int, fixture: str | None = None) -> tuple[list[dict], list[dict]]:
    ahora = datetime.now(timezone.utc)
    limite = ahora - timedelta(hours=horas)
    todas, estado = [], []
    fuentes = [("Tecnología", "Google Noticias", fixture)] if fixture else FUENTES
    for categoria, nombre, url in fuentes:
        try:
            data = Path(url).read_bytes() if fixture else descargar(url)
            items = parsear_rss(data, categoria, nombre)
            estado.append({"fuente": nombre, "categoria": categoria, "ok": True, "items": len(items)})
            todas.extend(items)
        except Exception as e:  # una fuente caída no detiene el resto
            estado.append({"fuente": nombre, "categoria": categoria, "ok": False, "error": str(e)[:160]})
    vistas, filtradas = set(), []
    for n in sorted(todas, key=lambda x: x["fecha"] or "", reverse=True):
        if n["fecha"] and datetime.fromisoformat(n["fecha"]) < limite and not fixture:
            continue
        cat = clasificar(n)
        if not cat:
            continue
        k = clave_dup(n["titulo"])
        if k in vistas or n["url"] in vistas:
            continue
        vistas.update({k, n["url"]})
        n["categoria"] = cat
        n["id"] = hashlib.sha1(n["url"].encode()).hexdigest()[:16]
        filtradas.append(n)
    # máximo 8 por categoría, las más recientes primero
    por_cat: dict[str, list] = {}
    for n in filtradas:
        por_cat.setdefault(n["categoria"], [])
        if len(por_cat[n["categoria"]]) < 8:
            por_cat[n["categoria"]].append(n)
    final = sorted([n for lst in por_cat.values() for n in lst], key=lambda x: x["fecha"] or "", reverse=True)
    return final, estado


def subir_supabase(noticias: list[dict]) -> str:
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")
    if not url or not key or not noticias:
        return "omitido (sin SUPABASE_URL/SUPABASE_KEY)"
    filas = [{"id": n["id"], "titulo": n["titulo"], "url": n["url"], "fuente": n["fuente"], "categoria": n["categoria"],
              "fecha": n["fecha"], "resumen": n["resumen"]} for n in noticias]
    req = urllib.request.Request(url.rstrip("/") + "/rest/v1/noticias?on_conflict=id", data=json.dumps(filas).encode(), method="POST",
                                 headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "Prefer": "resolution=merge-duplicates,return=minimal"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return f"ok ({r.status}, {len(filas)} filas)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--horas", type=int, default=48)
    ap.add_argument("--fixture", help="archivo RSS local para pruebas sin internet")
    ap.add_argument("--salida", default=str(SALIDA))
    a = ap.parse_args()

    noticias, estado = recolectar(a.horas, a.fixture)
    if not noticias and not a.fixture and Path(a.salida).exists():
        print("Sin noticias nuevas; se conserva el archivo anterior.")
        return 0
    doc = {
        "actualizado": datetime.now(BOGOTA).isoformat(timespec="seconds"),
        "ventana_horas": a.horas,
        "total": len(noticias),
        "categorias": sorted({n["categoria"] for n in noticias}),
        "fuentes": estado,
        "noticias": noticias,
    }
    Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
    Path(a.salida).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(noticias)} noticias guardadas en {a.salida}")
    for e in estado:
        print(("  ✔ " if e["ok"] else "  ✖ ") + f"{e['fuente']} [{e['categoria']}] " + (f"{e['items']} items" if e["ok"] else e["error"]))
    try:
        print("Supabase:", subir_supabase(noticias))
    except Exception as e:
        print("Supabase: error", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
