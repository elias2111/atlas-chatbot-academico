-- ATLAS · consultas para mostrar en la sustentación (Supabase → SQL Editor)

-- 1. Plan de estudios: créditos por semestre (debe sumar 151)
SELECT semestre, count(*) AS asignaturas, sum(creditos) AS creditos FROM asignatura GROUP BY semestre ORDER BY semestre;

-- 2. Prerrequisitos de una asignatura y lo que desbloquea
SELECT fn_prerrequisitos('Dinámica de sistemas');

-- 3. Estado académico completo del estudiante (lo que recibe el agente)
SELECT fn_contexto_estudiante('20221045');

-- 4. Avance y promedio
SELECT * FROM v_avance;

-- 5. Notas del semestre: nota actual, nota necesaria para 3,0 y estado
SELECT asignatura_nombre, peso_evaluado, acumulado, nota_actual, nota_necesaria, estado
FROM v_notas_semestre WHERE estudiante = '20221045' ORDER BY nota_actual;

-- 6. Tareas por categoría y próximas entregas
SELECT categoria, count(*) FROM v_tareas WHERE estudiante = '20221045' GROUP BY categoria;
SELECT titulo, asignatura_nombre, fecha_entrega, dias_para_entrega, categoria, progreso
FROM v_tareas WHERE estudiante = '20221045' AND categoria <> 'entregada' ORDER BY fecha_entrega;

-- 7. Noticias del día que dejó el scraper
SELECT categoria, fuente, titulo, fecha FROM v_noticias_hoy LIMIT 10;

-- 8. RAG: fragmentos cargados por documento (después de la ingesta en n8n)
SELECT metadata->>'source' AS documento, count(*) AS fragmentos FROM n8n_vectors GROUP BY 1;

-- 9. Memoria del agente: últimas conversaciones
SELECT session_id, left(message::text, 120) AS mensaje FROM n8n_chat_histories ORDER BY id DESC LIMIT 10;
