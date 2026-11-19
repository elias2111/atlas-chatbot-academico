# Base de datos PostgreSQL

Todo el modelo, los datos de ejemplo, las vistas y las funciones están en un solo script: **[`backend/schema.sql`](../backend/schema.sql)** (PostgreSQL 14+ con pgvector; probado en PostgreSQL 16). Las consultas para mostrar en la sustentación están en [`backend/consultas_demo.sql`](../backend/consultas_demo.sql).

## Modelo entidad-relación

```mermaid
erDiagram
  PROGRAMA ||--o{ ASIGNATURA : contiene
  PROGRAMA ||--o{ ESTUDIANTE : matricula
  ASIGNATURA ||--o{ PRERREQUISITO : "requiere"
  ASIGNATURA ||--o{ PRERREQUISITO : "es requisito de"
  ESTUDIANTE ||--o{ INSCRIPCION : cursa
  ASIGNATURA ||--o{ INSCRIPCION : "se inscribe en"
  ESTUDIANTE ||--o{ EVALUACION : "recibe nota"
  ASIGNATURA ||--o{ EVALUACION : evalua
  ESTUDIANTE ||--o{ TAREA : tiene
  ASIGNATURA ||--o{ TAREA : pertenece
  EVALUACION |o--o{ TAREA : "cuenta para"

  PROGRAMA { int id PK; text nombre; int creditos_total; int max_creditos_semestre }
  ASIGNATURA { text codigo PK; text nombre; int semestre; int creditos; text area }
  PRERREQUISITO { text asignatura FK; text requiere FK }
  ESTUDIANTE { text codigo PK; text nombre; int semestre_actual; text periodo_actual; text estado_matricula }
  INSCRIPCION { int id PK; text estudiante FK; text asignatura FK; text periodo; text estado; numeric nota; text nombre_electiva }
  EVALUACION { text id PK; text estudiante FK; text asignatura FK; text nombre; int corte; numeric peso; numeric nota; date fecha }
  TAREA { text id PK; text estudiante FK; text asignatura FK; text titulo; date fecha_entrega; text estado; int progreso; numeric nota }
  NOTICIAS { text id PK; text titulo; text url; text fuente; text categoria; timestamptz fecha }
```

Además, n8n crea solas `n8n_vectors` (pgvector, RAG) y `n8n_chat_histories` (memoria del agente).

## Tablas, vistas y funciones

| Objeto | Tipo | Qué guarda o calcula |
|---|---|---|
| `programa`, `asignatura`, `prerrequisito` | tablas | Plan de Ingeniería de Sistemas: **51 asignaturas, 151 créditos, 33 relaciones de prerrequisito** |
| `estudiante`, `inscripcion` | tablas | Matrícula y expediente (aprobadas con nota, cursando, reprobadas) |
| `evaluacion` | tabla | Notas del semestre por evaluación: corte, peso (%), nota 0,0–5,0 (39 filas de ejemplo) |
| `tarea` | tabla | Tareas con fecha, estado y avance (16 filas de ejemplo) |
| `noticias` | tabla | Noticias del día que llena el scraper |
| `v_avance` | vista | Créditos aprobados y en curso, y promedio por estudiante |
| `v_notas_semestre` | vista | Acumulado, nota actual, **nota necesaria para 3,0** y estado; definitiva **sin aproximar** (Art. 39, `TRUNC`) |
| `v_tareas` | vista | Días para la entrega y categoría (vencida, incompleta, por hacer, entregada) |
| `v_noticias_hoy` | vista | Noticias de las últimas 48 h |
| `fn_contexto_estudiante(codigo)` | función | JSON con todo el estado académico (la usan el agente y la herramienta MCP) |
| `fn_notas_semestre`, `fn_tareas`, `fn_prerrequisitos` | funciones | Consultas parametrizadas que expone el servidor MCP |

**Regla de cálculo clave** (`v_notas_semestre`):

```
acumulado      = Σ nota × peso / 100                       (evaluaciones calificadas)
nota_actual    = Σ nota × peso / Σ peso evaluado
nota_necesaria = (3,0 − acumulado) / (peso restante / 100)
estado         = APROBADA / REPROBADA (todas las notas, definitiva truncada a la décima)
               | APROBADA ASEGURADA (acumulado ≥ 3,0) | PERDIDA (ni con 5,0 llega) | EN RIESGO | APROBANDO
```

## Cómo montarla en Supabase (10 minutos)

1. Crea una cuenta en https://supabase.com, luego **New project** (región São Paulo o us-east) y guarda la contraseña.
2. Ve a **SQL Editor → New query**, pega todo `backend/schema.sql` y presiona **Run**. Al final debe decir "Success".
3. Verifica con [`backend/consultas_demo.sql`](../backend/consultas_demo.sql), por ejemplo:
   ```sql
   SELECT asignatura_nombre, nota_actual, nota_necesaria, estado FROM v_notas_semestre WHERE estudiante = '20221045';
   ```
4. Ve a **Project Settings → API** y copia la **URL** y la **anon key**:
   - en la app: Ajustes → Base de datos académica → **Conectar y descargar**;
   - en GitHub: Settings → Secrets → Actions → `SUPABASE_URL` y `SUPABASE_KEY` (así el scraper también guarda en la tabla `noticias`);
   - en el servidor MCP Python: variables `SUPABASE_URL` y `SUPABASE_KEY`.
5. Ve a **Project Settings → Database** y copia la cadena de conexión para la credencial **Postgres** de n8n (host `db.xxxx.supabase.co`, puerto 5432, usuario `postgres`, base de datos `postgres`, SSL activado).

**Evidencia para la rúbrica:** capturas del *Table Editor* con las tablas llenas (`asignatura`, `evaluacion`, `tarea`, `noticias`) y del *SQL Editor* con el resultado de `v_notas_semestre`.

## Datos de prueba ya verificados

Al ejecutar el script en PostgreSQL 16, `v_notas_semestre` devuelve exactamente lo mismo que calcula la app:

| Asignatura | Nota actual | Necesaria | Estado |
|---|---|---|---|
| Cálculo integral | 2,97 | 3,05 | EN RIESGO |
| Electromagnetismo y laboratorio | 3,44 | 2,34 | APROBANDO |
| Laboratorio de electromagnetismo | 4,23 | — | APROBADA ASEGURADA |
| Investigación de operaciones I | 4,03 | 1,45 | APROBANDO |
| Ciberseguridad | 4,17 | 1,25 | APROBANDO |
| Sistemas Inteligentes | 3,87 | 2,13 | APROBANDO |
| Marca Personal Digital | 4,53 | 0,71 | APROBANDO |
| Proyectos en ingeniería de sistemas II | 4,40 | 0,90 | APROBANDO |
