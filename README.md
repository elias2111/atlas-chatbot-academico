# ATLAS · Chatbot de apoyo académico con n8n

> **Trabajo final de Ciencia de Datos, Tema 2** · Ingeniería de Sistemas
> Autor: José Elías Cruz

**▶ App en vivo:** https://elias2111.github.io/atlas-chatbot-academico/
(ábrela en Safari desde el iPhone y toca **Compartir → Agregar a pantalla de inicio**)

ATLAS es un asistente académico **por voz**, al estilo de un mayordomo de IA, que apoya al estudiante de Ingeniería de Sistemas en:

1. **Estado de matrícula y avance del plan de estudios**: los 9 semestres y 151 créditos del plan oficial, más el **portal del semestre** con notas por corte, nota necesaria para aprobar y tareas.
2. **Proyección de semestres restantes y alertas de requisitos pendientes**: ruta crítica, rezago, carga, inglés y práctica.
3. **Recomendaciones personalizadas para el éxito académico**: educación de precisión, investigación y autoaprendizaje.
4. **Base conceptual**: chatbot institucional con **arquitectura RAG, n8n, PostgreSQL y app móvil**.

| Asistente de voz | Notas del semestre | Tareas | Avance | Ruta | Recomendaciones |
|:-:|:-:|:-:|:-:|:-:|:-:|
| ![](docs/1-asistente.png) | ![](docs/2-notas.png) | ![](docs/3-tareas.png) | ![](docs/4-avance.png) | ![](docs/5-proyeccion.png) | ![](docs/6-rumbo.png) |

---

## Arquitectura

```
 ┌──────────────────────────┐      POST {message, context}      ┌───────────────────────────────┐
 │  App móvil (PWA · iPhone) │ ────────────────────────────────▶ │ n8n · Webhook /atlas-chat     │
 │  • Voz: Web Speech API    │                                   │   ├─ PostgreSQL (expediente)  │
 │  • Expediente editable    │ ◀──────────────────────────────── │   ├─ Agente IA + memoria      │
 │  • Motor local offline    │            {reply}                │   └─ RAG: reglamento (pgvector)│
 └──────────────────────────┘                                   └───────────────────────────────┘
          │  sin n8n
          └──▶ IA directa (OpenAI) ──▶ o motor local de intenciones (sin internet)
```

La app tiene **tres niveles de inteligencia** y siempre usa el más alto disponible; si uno falla, pasa al siguiente:

| Nivel | Requiere | Qué hace |
|---|---|---|
| 1. Motor local | Nada (funciona sin internet) | Entiende preguntas sobre matrícula, avance, grado, requisitos, materias, promedio y recomendaciones, y comandos que actualizan el expediente |
| 2. IA directa | API key de OpenAI (Ajustes) | Preguntas abiertas respondidas con todo el expediente como contexto |
| 3. n8n + RAG | Flujo de `backend/` activo | Agente con memoria en PostgreSQL y búsqueda en el reglamento estudiantil |

## Funcionalidades

### Portal del semestre (base de datos de notas y tareas)
- **Notas por evaluación y corte** en la escala **0,0 – 5,0**: cada evaluación tiene un peso (%) y una nota. Para cada materia ATLAS calcula:
  - **Nota actual**: el promedio ponderado de lo evaluado.
  - **Acumulado**: los puntos ganados sobre 5,0.
  - **Nota necesaria**: la mínima que te falta sacar en lo restante para llegar a **3,0**, con la fórmula `(3,0 − acumulado) ÷ (peso restante)`.
  - **Estado**: *Aprobando*, *En riesgo*, *Aprobada asegurada* (ya tienes 3,0 acumulado), *Perdida* (ni con 5,0 alcanzas), y al final *Aprobada* o *Reprobada* con la definitiva redondeada a una décima.
- **Cierre automático**: cuando todas las evaluaciones de una materia tienen nota, la definitiva pasa sola al expediente y se recalculan el avance, la proyección y el grado.
- **Tareas**: con fecha de entrega, avance (%) y estado. Se clasifican en **por hacer**, **incompletas**, **vencidas** y **entregadas**, y se pueden vincular a una evaluación.
- **Alertas del semestre**: materias en riesgo o perdidas, tareas vencidas y entregas en las próximas 48 horas.
- **Base de datos**: funciona en el teléfono sin configurar nada, o conectada a **PostgreSQL en Supabase** por su API REST (Ajustes → Base de datos académica). Cada cambio se sincroniza solo.

### Asistente y expediente

- **Conversación por voz**: tocas el núcleo, hablas y ATLAS te responde en voz alta. Con la *conversación continua* vuelve a escucharte al terminar. Si tocas el núcleo mientras habla, lo interrumpes.
- **Expediente editable y persistente**: tocas cualquier materia y la marcas como Aprobada, Cursando, Pendiente o Reprobada, con su nota. A las electivas les pones el nombre real. Todo se recalcula al instante y se guarda en el teléfono. Se puede exportar e importar en JSON.
- **Comandos por voz**: "aprobé Cálculo integral con 4,2", "perdí Investigación de operaciones I", "estoy viendo Ecuaciones diferenciales", "cancelé…", "aprobé inglés B2.1".
- **Proyección inteligente**: arma los semestres restantes respetando los prerrequisitos y el límite de créditos por semestre (configurable), y calcula la fecha estimada de grado.
- **Alertas**: materias reprobadas, ruta crítica (por ejemplo, Cálculo integral bloquea a Ecuaciones diferenciales y a Dinámica de sistemas), prerrequisitos sin aprobar, carga alta, materias rezagadas, requisito de inglés, práctica y bases débiles.
- **Educación de precisión**: plan semanal de horas calculado con los créditos, la ruta crítica y tu rendimiento por área.
- **PWA instalable**: pantalla completa, ícono propio y funcionamiento sin conexión gracias al service worker.

## Probarla

**En el iPhone (para la demo)**
1. Abre https://elias2111.github.io/atlas-chatbot-academico/ en **Safari**.
2. Toca **Compartir → Agregar a pantalla de inicio** y ábrela desde el ícono.
3. Toca **INICIAR SISTEMA** y luego el núcleo. Permite el micrófono y el reconocimiento de voz.
4. Si iOS no deja usar la voz dentro de la app instalada, ábrela directamente en la pestaña de Safari o usa el micrófono del teclado. ATLAS igual responde en voz alta.

**En el computador**: abre la página en **Chrome** o **Edge**, sin VPN. Firefox y Opera no tienen reconocimiento de voz.

**Frases para probar**

| Dile a ATLAS | Resultado |
|---|---|
| "Dame el informe del semestre" | Promedio parcial, materias en riesgo, tareas y próximas entregas |
| "¿Cómo voy en Cálculo integral?" / "¿Aprobé Ciberseguridad?" | Nota actual, nota necesaria para 3,0 y estado |
| "¿Cuánto saqué en el parcial 2 de Cálculo integral?" | La nota de esa evaluación |
| "¿Cuándo es la sustentación del proyecto de grado?" | Fecha y peso |
| "¿Qué tareas tengo pendientes?" / "¿Tengo tareas vencidas?" / "¿Qué tengo para esta semana?" | Tareas filtradas |
| "Saqué 3,5 en el examen final de Electromagnetismo" | Registra la nota y te dice si aprobaste |
| "Entregué el informe de Faraday" / "Voy en el 80% del trabajo de inventarios" | Actualiza la tarea |
| "Explícame integración por partes" | Tutor de la materia (con IA conectada) |
| "¿Qué materias estoy viendo?" | Matrícula actual y créditos |
| "¿Cuándo me gradúo?" | Proyección semestre a semestre |
| "¿Qué requisitos tengo pendientes?" | Alertas priorizadas |
| "¿Puedo ver Dinámica de sistemas?" | Prerrequisitos y si está habilitada |
| "Aprobé Cálculo integral con 4,2" | Actualiza el expediente y recalcula todo |
| "Dame recomendaciones" / "Arma mi plan semanal" | Educación de precisión |
| "Abre mi ruta" | Navega a la pestaña Ruta |

## Backend (n8n + PostgreSQL)

```
backend/
├── schema.sql                 # plan de 151 créditos, expediente, notas (evaluacion), tareas (tarea), vistas v_notas_semestre y v_tareas
├── n8n_atlas_chat.json        # Webhook → Postgres → Agente IA (memoria + RAG) → respuesta
└── n8n_atlas_ingesta_rag.json # formulario para cargar el reglamento (PDF) a pgvector
```

1. Ejecuta `backend/schema.sql` en PostgreSQL con pgvector (Supabase o Neon). Para probarlo:
   `SELECT * FROM v_notas_semestre WHERE estudiante = '20221045';` y `SELECT * FROM v_tareas ORDER BY fecha_entrega;`
2. **Conectar la app a la base de datos**: en Supabase ve a *Project Settings → API*, copia la **URL** y la **anon key**, pégalas en la app en **Ajustes → Base de datos académica** y toca **Conectar y descargar**. Desde ese momento la app lee y escribe las notas y tareas en PostgreSQL.
3. En n8n, importa los dos JSON y asigna las credenciales de **Postgres** y **OpenAI**.
4. Activa *ATLAS · Ingesta RAG* y sube el reglamento estudiantil.
5. Activa *ATLAS · Chat académico* y copia la **Production URL** del Webhook en **Ajustes → Conexión n8n** de la app.

**Contrato de la API**

```http
POST /webhook/atlas-chat
{ "sessionId": "s-ab12cd34", "studentId": "20221045", "message": "¿Cuándo me gradúo?", "context": { ...expediente... } }

→ 200 { "reply": "Si aprueba lo que cursa, señor, se gradúa en 2027-2…" }
```

## Estructura del proyecto

```
├── index.html        # la app completa (HTML + CSS + JS, sin dependencias)
├── manifest.json     # instalación como app
├── sw.js             # service worker (red primero, caché sin conexión)
├── icons/            # íconos
├── docs/             # capturas
└── backend/          # n8n + PostgreSQL
```

## Notas

- **Plan de estudios**: las asignaturas y los créditos son los del plan oficial de Ingeniería de Sistemas. El plan no publica los prerrequisitos, así que la app usa una propuesta lógica; se ajusta en la constante `PLAN` de `index.html`.
- **Datos de ejemplo**: al abrir la app por primera vez se cargan datos de ejemplo. Las notas del semestre son inventadas; las tareas corresponden a proyectos reales del semestre. En **Avance → Usar mis datos** o **Empezar en blanco** se registra el expediente real.
- **Privacidad**: el expediente y la API key se guardan solo en el navegador del dispositivo (`localStorage`).
