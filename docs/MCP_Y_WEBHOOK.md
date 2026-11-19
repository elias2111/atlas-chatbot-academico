# Servidor MCP y webhook

## Servidor MCP

ATLAS expone su base de datos como herramientas **MCP (Model Context Protocol)**, que un agente de IA puede descubrir (`tools/list`) y llamar (`tools/call`). Hay dos implementaciones con las **mismas herramientas**:

| Implementación | Archivo | Transporte | Para qué |
|---|---|---|---|
| **MCP Server Trigger de n8n** | [`backend/n8n_atlas_mcp_server.json`](../backend/n8n_atlas_mcp_server.json) | SSE / HTTP en `https://TU-N8N/mcp/atlas` | Lo consume el agente del flujo de chat mediante el nodo *MCP Client Tool* |
| **Servidor MCP en Python** | [`mcp-server/atlas_mcp_server.py`](../mcp-server/atlas_mcp_server.py) | stdio y HTTP (`POST /mcp`) | Claude Desktop, MCP Inspector, curl o Postman. Solo usa la biblioteca estándar |

### Herramientas

| Herramienta | Parámetros | Consulta en PostgreSQL | Devuelve |
|---|---|---|---|
| `consultar_estado_academico` | `codigo` | `fn_contexto_estudiante($1)` | Programa, periodo, estado de matrícula, créditos aprobados y en curso, % de avance, PGA, materias en curso y pendientes con los prerrequisitos que faltan |
| `consultar_notas_semestre` | `codigo` | `fn_notas_semestre($1)` → `v_notas_semestre` | Por materia: evaluaciones (corte, peso, nota), nota actual, acumulado, nota necesaria para 3,0 y estado |
| `consultar_tareas` | `codigo`, `categoria?` | `fn_tareas($1, $2)` → `v_tareas` | Tareas con fecha, días restantes, estado, avance y categoría (vencida, incompleta, por hacer, entregada) |
| `consultar_prerrequisitos` | `asignatura` | `fn_prerrequisitos($1)` | Prerrequisitos y asignaturas que desbloquea |
| `noticias_del_dia` | `categoria?` | `v_noticias_hoy` | Noticias de las últimas 48 h con fuente, fecha y enlace |
| `buscar_reglamento` *(solo n8n)* | consulta | pgvector | Fragmentos del reglamento, del plan y de la guía (RAG) |

**Seguridad:**
- Todas las consultas son **parametrizadas** (`$1`, `$2` en n8n; variables `:'p1'` en psql). Ningún texto del usuario se concatena en el SQL.
- El servidor Python además **valida los parámetros**: código alfanumérico de máximo 20 caracteres y categorías de una lista cerrada.
- Las herramientas son de **solo lectura**.

### Probarlo

```bash
# Opción A: PostgreSQL directo
export DATABASE_URL="postgresql://postgres:CLAVE@db.xxxx.supabase.co:5432/postgres"
# Opción B: API REST de Supabase
export SUPABASE_URL="https://xxxx.supabase.co"; export SUPABASE_KEY="anon-key"

python mcp-server/probar_mcp.py                       # cliente de prueba por stdio (handshake + 7 llamadas)
python mcp-server/atlas_mcp_server.py --http 8765     # servidor HTTP
curl -s localhost:8765/health
curl -s -X POST localhost:8765/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"consultar_tareas","arguments":{"codigo":"20221045","categoria":"vencida"}}}'
```

La salida completa de las pruebas está en **[`mcp-server/EVIDENCIA_PRUEBAS.md`](../mcp-server/EVIDENCIA_PRUEBAS.md)**: 7 de 7 casos con el comportamiento esperado, incluido un intento de inyección SQL rechazado y un estudiante inexistente.

**Conectarlo a Claude Desktop** (`claude_desktop_config.json`):

```json
{ "mcpServers": { "atlas": {
    "command": "python3",
    "args": ["/ruta/atlas-chatbot-academico/mcp-server/atlas_mcp_server.py"],
    "env": { "SUPABASE_URL": "https://xxxx.supabase.co", "SUPABASE_KEY": "anon-key" } } } }
```

## Webhooks de n8n

| Endpoint | Método | Flujo | Entrada | Salida |
|---|---|---|---|---|
| `/webhook/atlas-chat` | POST | Chat académico | `{ sessionId, studentId, message, context }` | `{ reply, guardrails }` |
| `/webhook/atlas-noticias` | GET | Scraper de noticias | — | lista de noticias de las últimas 48 h |
| `/mcp/atlas` | SSE/HTTP | Servidor MCP | protocolo MCP | herramientas |

### Pruebas del webhook

- **curl**: [`tests/probar_webhook.sh`](../tests/probar_webhook.sh) hace 6 pruebas: conexión, estado académico, notas, reglamento (RAG), noticias y 2 ataques que los guardrails deben bloquear.
  ```bash
  N8N_URL="https://TU-N8N" bash tests/probar_webhook.sh
  ```
- **Postman**: importa [`tests/ATLAS.postman_collection.json`](../tests/ATLAS.postman_collection.json) y cambia la variable `n8n_url`.
- **App**: Ajustes → Conexión n8n → pega la URL → **Probar conexión**. Cada mensaje muestra "n8n · RAG" como origen de la respuesta.

Guarda como evidencia la salida de curl o la captura de Postman, y el registro de ejecución de n8n (*Executions*), donde se ve qué herramientas llamó el agente.
