# Scraper de noticias del día

El scraper muestra en la app y le entrega al agente las **noticias del día sobre educación, tecnología e ingeniería de sistemas**, siempre con **fuente y fecha**.

## Dos implementaciones equivalentes

| | GitHub Actions (en producción) | n8n |
|---|---|---|
| Código | [`scraper/scraper_noticias.py`](../scraper/scraper_noticias.py) (Python, solo biblioteca estándar) | [`backend/n8n_atlas_scraper_noticias.json`](../backend/n8n_atlas_scraper_noticias.json) |
| Programación | [`.github/workflows/scraper-noticias.yml`](../.github/workflows/scraper-noticias.yml): todos los días a las **6:00 y 13:00** (hora de Colombia), y a mano con *Run workflow* | Schedule Trigger `0 6,13 * * *` |
| Salida | [`data/noticias.json`](../data/noticias.json) publicado en GitHub Pages; también la tabla `noticias` si existen los secretos `SUPABASE_URL` y `SUPABASE_KEY` | Tabla `noticias` + endpoint `GET /webhook/atlas-noticias` |
| Integración | La **app** lo carga en *Rumbo → Noticias del día* y responde "noticias de tecnología de hoy". La IA directa lo recibe en el contexto | Herramienta MCP `noticias_del_dia` del **agente** |

## Proceso

1. **Fuentes RSS**: Google Noticias Colombia (es-419), con 5 búsquedas sobre ingeniería de sistemas, software, ciberseguridad, inteligencia artificial, educación superior, ICETEX y Saber Pro, más el feed de Xataka.
2. **Descarga**: tolera fallos, porque una fuente caída se registra y no detiene el resto.
3. **Limpieza**: quita HTML, separa el medio del título ("… - El Tiempo" → fuente: El Tiempo) y normaliza la fecha a ISO-8601.
4. **Filtro temporal**: solo noticias de las **últimas 48 horas**.
5. **Clasificación** por palabras clave en *Educación*, *Tecnología* o *Ingeniería de sistemas*. Lo que no encaja se descarta (por ejemplo, una receta de cocina).
6. **Sin duplicados**: compara la URL y una huella de las palabras del título, porque la misma noticia publicada por dos medios cuenta una sola vez.
7. **Límite**: 8 noticias por categoría, las más recientes primero.
8. **Publicación**: guarda el JSON y hace el *upsert* en PostgreSQL.

## Evidencia

- **Ejecuciones automáticas**: https://github.com/elias2111/atlas-chatbot-academico/actions/workflows/scraper-noticias.yml. Cada ejecución deja su registro y un commit "Noticias del día AAAA-MM-DD HH:MM".
- **Primera ejecución** (18/11/2026, 23:58): **24 noticias** de 6 fuentes, todas respondieron (11, 9, 43, 26, 27 y 5 artículos leídos antes de filtrar).
- **Prueba sin conexión** con un RSS de ejemplo: `python scraper/scraper_noticias.py --fixture scraper/pruebas/rss_prueba.xml --salida /tmp/n.json`. Comprueba que separa el medio del título, quita el duplicado y descarta lo que no es pertinente.

```bash
python scraper/scraper_noticias.py            # ejecuta el scraper (últimas 48 h)
python scraper/scraper_noticias.py --horas 24
```
