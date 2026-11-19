#!/usr/bin/env python3
"""
ATLAS · RAG local: fragmentación, índice y evaluación de la recuperación
=======================================================================
Usa EXACTAMENTE los mismos parámetros de fragmentación del flujo de n8n
(RecursiveCharacterTextSplitter: 1.000 caracteres, 150 de solapamiento) y un
recuperador léxico BM25 que también corre dentro de la app (sin internet ni API key).
En n8n la recuperación es semántica (embeddings text-embedding-3-small + pgvector);
este script sirve para construir el índice de la app y para medir la calidad.

  python rag/rag_local.py build   # genera data/rag_index.json (lo carga la app)
  python rag/rag_local.py eval    # corre las consultas de prueba y escribe rag/EVIDENCIA_RECUPERACION.md
  python rag/rag_local.py ask "¿puedo habilitar con 2,6?"
"""
from __future__ import annotations

import json
import math
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "rag" / "docs"
INDICE = RAIZ / "data" / "rag_index.json"
CHUNK_SIZE, CHUNK_OVERLAP = 1000, 150
SEPARADORES = ["\n\n", "\n- ", ". ", " "]
K1, B = 1.5, 0.75
STOP = set("""a al algo ante antes como con contra cual cuando de del desde donde dos el ella ellas ellos en entre era es esa ese
eso esta este esto estos fue ha hay la las le les lo los mas me mi mis muy ni no nos o otra otro para pero por porque que quien se
sea si sin sobre su sus tambien te tiene tu un una uno unos y ya yo puedo hago cuanto cuantos cuantas cual cuales debo tengo""".split())


def normalizar(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")


def raiz(w: str) -> str:
    """Stemming ligero para español (plurales y terminaciones verbales frecuentes)."""
    for suf in ("aciones", "acion", "amente", "mente", "idades", "idad", "ables", "able", "ando", "iendo", "ados", "idas", "ido", "ada", "ado",
                "ar", "er", "ir", "es", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def tokens(t: str) -> list[str]:
    return [raiz(w) for w in re.findall(r"[a-z0-9]+", normalizar(t)) if w not in STOP and len(w) > 1]


# ------------------------------------------------------------------ fragmentación
def dividir(texto: str, seps=SEPARADORES) -> list[str]:
    if len(texto) <= CHUNK_SIZE:
        return [texto]
    sep = next((s for s in seps if s in texto), "")
    partes = texto.split(sep) if sep else [texto[i:i + CHUNK_SIZE] for i in range(0, len(texto), CHUNK_SIZE)]
    piezas = []
    for p in partes:
        p = (p + (sep if sep.strip() == "." else "")).strip()
        if not p:
            continue
        piezas.extend(dividir(p, seps[seps.index(sep) + 1:] if sep in seps else seps) if len(p) > CHUNK_SIZE else [p])
    # unir piezas hasta CHUNK_SIZE con solapamiento de CHUNK_OVERLAP caracteres
    chunks, actual = [], ""
    unir = "\n" if sep in ("\n\n", "\n- ") else " "
    for p in piezas:
        if sep == "\n- ":
            p = "- " + p.lstrip("- ")
        if actual and len(actual) + len(unir) + len(p) > CHUNK_SIZE:
            chunks.append(actual.strip())
            cola = actual[-CHUNK_OVERLAP:]
            cola = cola[cola.find(" ") + 1:] if " " in cola else cola
            actual = cola + unir + p
        else:
            actual = (actual + unir + p) if actual else p
    if actual.strip():
        chunks.append(actual.strip())
    return chunks


def fragmentar_documento(ruta: Path) -> list[dict]:
    texto = ruta.read_text(encoding="utf-8")
    titulo = texto.splitlines()[0].lstrip("# ").strip()
    secciones = re.split(r"\n(?=## )", texto)
    out = []
    for sec in secciones:
        lineas = sec.strip().splitlines()
        if not lineas:
            continue
        encabezado = lineas[0].lstrip("# ").strip()
        cuerpo = "\n".join(lineas[1:]).strip() if lineas[0].startswith("#") else sec.strip()
        if not cuerpo:
            continue
        for i, ch in enumerate(dividir(cuerpo)):
            out.append({"doc": ruta.stem, "titulo_doc": titulo, "seccion": encabezado, "parte": i + 1, "texto": ch})
    return out


# ------------------------------------------------------------------ BM25
class BM25:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.docs = [tokens(c["seccion"] + " " + c["seccion"] + " " + c["texto"]) for c in chunks]  # el título de sección pesa doble
        self.avgdl = sum(map(len, self.docs)) / max(1, len(self.docs))
        df = Counter(t for d in self.docs for t in set(d))
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self.tf = [Counter(d) for d in self.docs]

    def buscar(self, consulta: str, k: int = 4):
        q = tokens(consulta)
        res = []
        for i, tf in enumerate(self.tf):
            dl = len(self.docs[i])
            s = sum(self.idf.get(t, 0) * tf[t] * (K1 + 1) / (tf[t] + K1 * (1 - B + B * dl / self.avgdl)) for t in q if t in tf)
            if s > 0:
                res.append((s, i))
        res.sort(reverse=True)
        return [(round(s, 3), self.chunks[i]) for s, i in res[:k]]


def construir() -> dict:
    chunks = []
    for ruta in sorted(DOCS.glob("*.md")):
        chunks.extend(fragmentar_documento(ruta))
    for i, c in enumerate(chunks):
        c["id"] = f"c{i:03d}"
    idx = {"generado": datetime.now().isoformat(timespec="seconds"),
           "parametros": {"chunk_size": CHUNK_SIZE, "chunk_overlap": CHUNK_OVERLAP, "separadores": SEPARADORES,
                          "recuperador_app": "BM25 (k1=1.5, b=0.75)", "recuperador_n8n": "pgvector coseno, text-embedding-3-small, top-k 4"},
           "documentos": sorted({c["titulo_doc"] for c in chunks}),
           "chunks": chunks}
    INDICE.parent.mkdir(parents=True, exist_ok=True)
    INDICE.write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")
    return idx


PRUEBAS = [
    ("¿Con qué nota se aprueba una materia?", "Escala de calificaciones"),
    ("Saqué 2,6 de definitiva, ¿puedo habilitar?", "Habilitaciones"),
    ("¿Cuántas veces puedo cancelar la misma materia?", "Cancelación"),
    ("¿Qué pasa si tengo muchas fallas en una clase?", "Asistencia"),
    ("¿Qué requisitos necesito para graduarme?", "Requisitos de grado"),
    ("¿Qué es la prueba académica y cuándo pierdo el cupo?", "prueba académica"),
    ("¿La nota definitiva se redondea?", "Redondeo"),
    ("No pude presentar el parcial porque estaba enfermo, ¿qué hago?", "supletorios"),
    ("¿Qué prerrequisitos tiene Dinámica de sistemas?", "Octavo semestre"),
    ("¿Qué técnicas de estudio funcionan mejor según la evidencia?", "Técnicas de estudio"),
    ("¿Cómo se calcula la nota que necesito para pasar?", "nota necesaria"),
    ("¿Qué es la educación de precisión?", "Educación de precisión"),
]


def evaluar(idx: dict) -> str:
    bm = BM25(idx["chunks"])
    top1 = top3 = 0
    filas, detalle = [], []
    for q, esperado in PRUEBAS:
        r = bm.buscar(q, 3)
        secs = [c["seccion"] for _, c in r]
        h1 = bool(secs) and esperado.lower() in secs[0].lower()
        h3 = any(esperado.lower() in s.lower() for s in secs)
        top1 += h1; top3 += h3
        filas.append(f"| {q} | {esperado} | {secs[0] if secs else '—'} | {r[0][0] if r else 0} | {'✔' if h1 else '✖'} | {'✔' if h3 else '✖'} |")
        detalle.append(f"### {q}\n" + "\n".join(f"{i+1}. **{c['titulo_doc']} › {c['seccion']}** (score {s})  \n   > {c['texto'][:260].replace(chr(10), ' ')}…" for i, (s, c) in enumerate(r)))
    n = len(PRUEBAS)
    tam = [len(c["texto"]) for c in idx["chunks"]]
    md = f"""# Evidencia de recuperación del RAG

Generado con `python rag/rag_local.py eval` el {datetime.now().strftime('%d/%m/%Y %H:%M')}.

## Corpus e índice

- Documentos: {", ".join(idx["documentos"])}
- Fragmentos: **{len(tam)}** · tamaño promedio {sum(tam)//len(tam)} caracteres (mín. {min(tam)}, máx. {max(tam)})
- Parámetros: `chunk_size = {CHUNK_SIZE}`, `chunk_overlap = {CHUNK_OVERLAP}`, separadores {SEPARADORES}
- Recuperador evaluado: BM25 (el mismo que corre en la app). En n8n se usa búsqueda semántica con `text-embedding-3-small` + pgvector (top-k 4).

## Resultados ({n} consultas)

| Métrica | Valor |
|---|---|
| Acierto en el 1.er resultado (precisión@1) | **{top1}/{n} = {top1/n:.0%}** |
| Acierto entre los 3 primeros (recall@3) | **{top3}/{n} = {top3/n:.0%}** |

| Consulta | Sección esperada | 1.er resultado | Score | @1 | @3 |
|---|---|---|---|---|---|
""" + "\n".join(filas) + "\n\n## Fragmentos recuperados por consulta\n\n" + "\n\n".join(detalle) + "\n"
    (RAIZ / "rag" / "EVIDENCIA_RECUPERACION.md").write_text(md, encoding="utf-8")
    return f"precisión@1 = {top1}/{n} · recall@3 = {top3}/{n}"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    idx = construir()
    print(f"Índice: {len(idx['chunks'])} fragmentos de {len(idx['documentos'])} documentos → {INDICE.relative_to(RAIZ)}")
    if cmd == "eval":
        print(evaluar(idx))
    elif cmd == "ask":
        for s, c in BM25(idx["chunks"]).buscar(" ".join(sys.argv[2:]), 3):
            print(f"[{s}] {c['titulo_doc']} › {c['seccion']}\n  {c['texto'][:300]}\n")
