# Evidencia de pruebas del servidor MCP

Pruebas ejecutadas contra PostgreSQL 16 con `backend/schema.sql` cargado (estudiante de ejemplo 20221045) y las 24 noticias reales que publicó el scraper el 19/11/2026.

## 1. Transporte stdio (`python mcp-server/probar_mcp.py`)

Handshake MCP → `tools/list` → 7 llamadas a herramientas (incluye un intento de inyección SQL y un estudiante inexistente, que deben fallar de forma controlada).

```text

→ {"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "probar_mcp", "version": "1"}}, "id": 1}
← {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-03-26", "capabilities": {"tools": {"listChanged": false}}, "serverInfo": {"name": "atlas-academico", "version": "1.0.0"}, "instructions": "Herramientas de solo lectura sobre la base de datos académica de ATLAS (Ingeniería de Sistemas, UNAB)."}}

→ {"jsonrpc": "2.0", "method": "notifications/initialized"}

→ {"jsonrpc": "2.0", "method": "tools/list", "id": 2}
← {"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": "consultar_estado_academico", "description": "Estado académico completo del estudiante: programa, periodo, estado de matrícula, créditos aprobados y en curso, porcentaje de avance, promedio (PGA), materias en curso y pendientes con los prerrequisitos que le faltan.", "inputSchema": {"type": "object", "properties": {"codigo": {"type": "string", "description": "Código del estudiante, p. ej. 20221045"}}, "required": ["codigo"]}}, {"name": "consultar_notas_semestre", "description": "Notas del semestre actual por materia en escala 0,0–5,0: evaluaciones (corte, peso, nota), nota actual, acumulado, nota necesaria para aprobar con 3,0 y estado (APROBANDO, EN RIESGO, APROBADA ASEGURADA, PERDIDA, APROBADA, REPROBADA).", "inputSchema": {"type": "object", "properties": {"codigo": {"type": "string"}}, "required": ["codigo"]}}, {"name": "consul …

# 5 herramientas: consultar_estado_academico, consultar_notas_semestre, consultar_tareas, consultar_prerrequisitos, noticias_del_dia

→ {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "consultar_estado_academico", "arguments": {"codigo": "20221045"}}, "id": 3}
← {"jsonrpc": "2.0", "id": 3, "result": {"content": [{"type": "text", "text": "{\"estudiante\": \"José Elías Cruz\", \"codigo\": \"20221045\", \"programa\": \"Ingeniería de Sistemas\", \"periodo_actual\": \"2026-2\", \"estado_matricula\": \"ACTIVA\", \"creditos_aprobados\": 95, \"creditos_en_curso\": 23, \"creditos_total\": 151, \"porcentaje_avance\": 62.9, \"promedio\": 4.2, \"promedio_por_area\": {\"Humanidades\": 4.46, \"Matemáticas\": 3.38, \"Proyectos\": 4.6, \"Electivas\": 3.93, \"Física\": 3.3, \"Seminarios\": 4.35, \"Sistemas\": 4.43, \"Bienestar\": 4.43}, \"cursando\": [{\"codigo\": \"CINT\", \"nombre\": \"Cálculo integral\", \"creditos\": 4}, {\"codigo\": \"ELEC\", \"nombre\": \"Electromagnetismo y laboratorio\", \"creditos\": 3}, {\"codigo\": \"LELE\", \"nombre\": \"Laboratorio de electromagnetismo\", \"creditos\": 0}, {\"codigo\": \"CIBS\", \"nombre\": \"Ciberseguridad\", \"cre …

→ {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "consultar_notas_semestre", "arguments": {"codigo": "20221045"}}, "id": 4}
← {"jsonrpc": "2.0", "id": 4, "result": {"content": [{"type": "text", "text": "[{\"asignatura\": \"Ciberseguridad\", \"estado\": \"APROBANDO\", \"nota_actual\": 4.17, \"acumulado\": 2.5, \"porcentaje_evaluado\": 60.0, \"nota_necesaria\": 1.25, \"evaluaciones\": [{\"nombre\": \"Parcial 1\", \"corte\": 1, \"peso\": 20.0, \"nota\": 3.9, \"fecha\": \"2026-09-16\"}, {\"nombre\": \"Laboratorio TryHackMe\", \"corte\": 1, \"peso\": 10.0, \"nota\": 4.6, \"fecha\": \"2026-09-25\"}, {\"nombre\": \"Parcial 2\", \"corte\": 2, \"peso\": 20.0, \"nota\": 4.1, \"fecha\": \"2026-10-20\"}, {\"nombre\": \"Informe de riesgos MAGERIT\", \"corte\": 2, \"peso\": 10.0, \"nota\": 4.4, \"fecha\": \"2026-10-29\"}, {\"nombre\": \"Hackathon CyberRisk 2.0\", \"corte\": 3, \"peso\": 20.0, \"nota\": null, \"fecha\": \"2026-11-23\"}, {\"nombre\": \"Examen final\", \"corte\": 3, \"peso\": 20.0, \"nota\": null, \"fecha\": \" …

→ {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "consultar_tareas", "arguments": {"codigo": "20221045", "categoria": "vencida"}}, "id": 5}
← {"jsonrpc": "2.0", "id": 5, "result": {"content": [{"type": "text", "text": "[{\"tarea\": \"Dataset etiquetado en Roboflow\", \"asignatura\": \"Sistemas Inteligentes\", \"entrega\": \"2026-11-17\", \"dias_para_entrega\": -2, \"estado\": \"en_progreso\", \"categoria\": \"vencida\", \"avance\": 70}, {\"tarea\": \"Taller 5: volúmenes de sólidos de revolución\", \"asignatura\": \"Cálculo integral\", \"entrega\": \"2026-11-18\", \"dias_para_entrega\": -1, \"estado\": \"pendiente\", \"categoria\": \"vencida\", \"avance\": 0}]"}], "isError": false}}

→ {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "consultar_prerrequisitos", "arguments": {"asignatura": "Dinámica de sistemas"}}, "id": 6}
← {"jsonrpc": "2.0", "id": 6, "result": {"content": [{"type": "text", "text": "{\"asignatura\": \"Dinámica de sistemas\", \"codigo\": \"DSIS\", \"semestre\": 8, \"creditos\": 3, \"prerrequisitos\": [{\"codigo\": \"EDIF\", \"nombre\": \"Ecuaciones diferenciales\"}, {\"codigo\": \"TSOR\", \"nombre\": \"Teoría de sistemas y organizaciones\"}], \"desbloquea\": []}"}], "isError": false}}

→ {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "noticias_del_dia", "arguments": {"categoria": "Educación"}}, "id": 7}
← {"jsonrpc": "2.0", "id": 7, "result": {"content": [{"type": "text", "text": "[{\"titulo\": \"Requisitos, universidades y más datos de Jóvenes a la E-6 en Bogotá\", \"fuente\": \"Bogota.gov.co\", \"categoria\": \"Educación\", \"fecha\": \"2026-11-18T23:11:55-05:00\", \"url\": \"https://news.google.com/rss/articles/CBMitAFBVV95cUxQc1FYVEhCV3RBZDJKaFd5LWNIanVJbENUZTNZZ1ppNHN2RzNIckswQ216YUNJWFpodVV3YWZIQnBIUmNTR2VDN3F1UUYxYnhDYXVrVnVfcUl6dmkwRG8wdm03QWRPd0hPeVdiNkdTcVVsanVpWEtHdHk5WFRuVUpnT3h1RmREY0xUNElLNG5uelhDQ2k2QjJlWkRySDlrQnpnOW5EN0oxNms2cklVemJoRm5DY2M?oc=5\"}, {\"titulo\": \"Unicórdoba nuevamente se destaca entre las universidades del país por su reputación académica y reconocimiento de empleadores en el QS 2027\", \"fuente\": \"ELHERALDO.CO\", \"categoria\": \"Educación\", \"fecha\": \"2026-11-18T16:40:03-05:00\", \"url\": \"https://news.google.com/rss/articles/CBMikwJBVV95cUxNbGpU …

→ {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "consultar_tareas", "arguments": {"codigo": "20221045'; DROP TABLE tarea;--"}}, "id": 8}
← {"jsonrpc": "2.0", "id": 8, "result": {"content": [{"type": "text", "text": "El parámetro 'codigo' debe ser alfanumérico (máx. 20 caracteres)."}], "isError": true}}

→ {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "consultar_estado_academico", "arguments": {"codigo": "99999999"}}, "id": 9}
← {"jsonrpc": "2.0", "id": 9, "result": {"content": [{"type": "text", "text": "No existe un estudiante con código 99999999."}], "isError": true}}

# Resultado: 7/7 casos con el comportamiento esperado
```

## 2. Transporte HTTP con curl (`python mcp-server/atlas_mcp_server.py --http 8765`)

```text
$ curl -s http://localhost:8765/health
{"ok": true, "server": {"name": "atlas-academico", "version": "1.0.0"}, "tools": ["consultar_estado_academico", "consultar_notas_semestre", "consultar_tareas", "consultar_prerrequisitos", "noticias_del_dia"]}

$ curl -s -X POST http://localhost:8765/mcp -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | jq '.result.tools[].name'
consultar_estado_academico
consultar_notas_semestre
consultar_tareas
consultar_prerrequisitos
noticias_del_dia

$ curl -s -X POST http://localhost:8765/mcp -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"consultar_notas_semestre","arguments":{"codigo":"20221045"}}}'
Ciberseguridad                           APROBANDO            actual=4.17 necesaria=1.25
Cálculo integral                         EN RIESGO            actual=2.97 necesaria=3.05
Marca Personal Digital                   APROBANDO            actual=4.53 necesaria=0.71
Electromagnetismo y laboratorio          APROBANDO            actual=3.44 necesaria=2.34
Sistemas Inteligentes                    APROBANDO            actual=3.87 necesaria=2.13
Investigación de operaciones I           APROBANDO            actual=4.03 necesaria=1.45
Laboratorio de electromagnetismo         APROBADA ASEGURADA   actual=4.23 necesaria=-0.7
Proyectos en ingeniería de sistemas II   APROBANDO            actual=4.4 necesaria=0.9
```
