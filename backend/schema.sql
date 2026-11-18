-- =====================================================================
-- ATLAS · Chatbot de apoyo académico — Esquema PostgreSQL
-- Plan de estudios: Ingeniería de Sistemas (9 semestres · 151 créditos)
-- Ejecutar en PostgreSQL 14+ (Supabase, Neon, Railway o local)
-- =====================================================================
CREATE EXTENSION IF NOT EXISTS vector;   -- pgvector, para el RAG del reglamento

DROP TABLE IF EXISTS inscripcion, prerrequisito, asignatura, estudiante, programa CASCADE;

CREATE TABLE programa (
  id              SERIAL PRIMARY KEY,
  nombre          TEXT NOT NULL,
  creditos_total  INT  NOT NULL,
  max_creditos_semestre INT NOT NULL DEFAULT 18
);

CREATE TABLE asignatura (
  codigo     TEXT PRIMARY KEY,
  programa_id INT REFERENCES programa(id),
  nombre     TEXT NOT NULL,
  semestre   INT  NOT NULL,
  creditos   INT  NOT NULL,
  area       TEXT NOT NULL
);

CREATE TABLE prerrequisito (
  asignatura    TEXT REFERENCES asignatura(codigo),
  requiere      TEXT REFERENCES asignatura(codigo),
  PRIMARY KEY (asignatura, requiere)
);

CREATE TABLE estudiante (
  codigo        TEXT PRIMARY KEY,
  nombre        TEXT NOT NULL,
  programa_id   INT REFERENCES programa(id),
  semestre_actual INT,
  periodo_actual TEXT NOT NULL,
  estado_matricula TEXT NOT NULL DEFAULT 'ACTIVA'   -- ACTIVA | INACTIVA | APLAZADA
);

CREATE TABLE inscripcion (
  id          SERIAL PRIMARY KEY,
  estudiante  TEXT REFERENCES estudiante(codigo),
  asignatura  TEXT REFERENCES asignatura(codigo),
  periodo     TEXT NOT NULL,
  estado      TEXT NOT NULL CHECK (estado IN ('aprobada','cursando','reprobada','cancelada')),
  nota        NUMERIC(3,1),
  nombre_electiva TEXT          -- p. ej. 'Sistemas Inteligentes' para una electiva de profundización
);
CREATE INDEX ON inscripcion (estudiante);

INSERT INTO programa (id, nombre, creditos_total) VALUES (1, 'Ingeniería de Sistemas', 151);

-- Plan de estudios oficial (9 semestres, 151 créditos). Prerrequisitos: propuesta editable.
INSERT INTO asignatura (codigo, programa_id, nombre, semestre, creditos, area) VALUES
  ('ALIN', 1, 'Álgebra lineal', 1, 3, 'Matemáticas'),
  ('CDIF', 1, 'Cálculo diferencial', 1, 4, 'Matemáticas'),
  ('EXPR', 1, 'Expresión', 1, 4, 'Humanidades'),
  ('FPRO', 1, 'Fundamentos de programación', 1, 3, 'Sistemas'),
  ('SEM1', 1, 'Seminario de ingeniería I', 1, 2, 'Seminarios'),
  ('CINT', 1, 'Cálculo integral', 2, 4, 'Matemáticas'),
  ('DIUS', 1, 'Diseño de interfaces de usuario', 2, 3, 'Sistemas'),
  ('IDEN', 1, 'Identidad', 2, 3, 'Humanidades'),
  ('LMEC', 1, 'Laboratorio de mecánica', 2, 0, 'Física'),
  ('MECL', 1, 'Mecánica y laboratorio', 2, 3, 'Física'),
  ('PCOM', 1, 'Programación de computadores', 2, 3, 'Sistemas'),
  ('TDRC', 1, 'Taller de deportes, recreación y cultura', 2, 1, 'Bienestar'),
  ('TDHU', 1, 'Taller de desarrollo humano', 2, 1, 'Bienestar'),
  ('CVAR', 1, 'Cálculo en varias variables', 3, 3, 'Matemáticas'),
  ('CREA', 1, 'Creatividad', 3, 3, 'Humanidades'),
  ('ELEC', 1, 'Electromagnetismo y laboratorio', 3, 3, 'Física'),
  ('EDAA', 1, 'Estructura de datos y análisis de algoritmos', 3, 3, 'Sistemas'),
  ('LELE', 1, 'Laboratorio de electromagnetismo', 3, 0, 'Física'),
  ('MCOM', 1, 'Matemáticas computacionales', 3, 3, 'Matemáticas'),
  ('SEM2', 1, 'Seminario de ingeniería II', 3, 2, 'Seminarios'),
  ('BD1', 1, 'Base de datos I', 4, 3, 'Sistemas'),
  ('DMUL', 1, 'Desarrollo multimedia', 4, 3, 'Sistemas'),
  ('EDIF', 1, 'Ecuaciones diferenciales', 4, 3, 'Matemáticas'),
  ('ESTG', 1, 'Estadística general', 4, 3, 'Matemáticas'),
  ('IART', 1, 'Inteligencia artificial', 4, 3, 'Sistemas'),
  ('TMOV', 1, 'Tecnologías móviles', 4, 3, 'Sistemas'),
  ('ALRD', 1, 'Actividades libres de recreación, deporte, cultura y desarrollo humano', 5, 2, 'Bienestar'),
  ('ASOF', 1, 'Arquitectura de software', 5, 3, 'Sistemas'),
  ('BD2', 1, 'Base de datos II', 5, 3, 'Sistemas'),
  ('EPR1', 1, 'Electiva de profundización I', 5, 3, 'Electivas'),
  ('INFT', 1, 'Infraestructura tecnológica', 5, 3, 'Sistemas'),
  ('ISW1', 1, 'Ingeniería de software I', 5, 3, 'Sistemas'),
  ('CDAT', 1, 'Ciencias de datos', 6, 3, 'Sistemas'),
  ('EPR2', 1, 'Electiva de profundización II', 6, 3, 'Electivas'),
  ('ETIC', 1, 'Ética de la ingeniería de sistemas', 6, 2, 'Humanidades'),
  ('ISW2', 1, 'Ingeniería de software II', 6, 3, 'Sistemas'),
  ('IOT', 1, 'Internet de las cosas', 6, 3, 'Sistemas'),
  ('TSOR', 1, 'Teoría de sistemas y organizaciones', 6, 3, 'Sistemas'),
  ('CIBS', 1, 'Ciberseguridad', 7, 3, 'Sistemas'),
  ('ESH1', 1, 'Electiva sociohumanística I', 7, 3, 'Electivas'),
  ('ECX1', 1, 'Electiva de contexto I', 7, 3, 'Electivas'),
  ('EPR3', 1, 'Electiva de profundización III', 7, 3, 'Electivas'),
  ('IOP1', 1, 'Investigación de operaciones I', 7, 3, 'Optimización'),
  ('PIS1', 1, 'Proyectos en ingeniería de sistemas I', 7, 2, 'Proyectos'),
  ('DSIS', 1, 'Dinámica de sistemas', 8, 3, 'Sistemas'),
  ('ESH2', 1, 'Electiva sociohumanística II', 8, 3, 'Electivas'),
  ('EPR4', 1, 'Electiva de profundización IV', 8, 3, 'Electivas'),
  ('IOP2', 1, 'Investigación de operaciones II', 8, 3, 'Optimización'),
  ('PIS2', 1, 'Proyectos en ingeniería de sistemas II', 8, 4, 'Proyectos'),
  ('ECX2', 1, 'Electiva de contexto II', 9, 3, 'Electivas'),
  ('PRAC', 1, 'Práctica en ingeniería de sistemas', 9, 12, 'Proyectos');

INSERT INTO prerrequisito (asignatura, requiere) VALUES
  ('CINT', 'CDIF'),
  ('MECL', 'CDIF'),
  ('PCOM', 'FPRO'),
  ('CVAR', 'CINT'),
  ('ELEC', 'MECL'),
  ('EDAA', 'PCOM'),
  ('LELE', 'MECL'),
  ('MCOM', 'ALIN'),
  ('MCOM', 'FPRO'),
  ('SEM2', 'SEM1'),
  ('BD1', 'EDAA'),
  ('DMUL', 'DIUS'),
  ('EDIF', 'CINT'),
  ('ESTG', 'CDIF'),
  ('IART', 'EDAA'),
  ('IART', 'MCOM'),
  ('TMOV', 'PCOM'),
  ('ASOF', 'EDAA'),
  ('BD2', 'BD1'),
  ('ISW1', 'BD1'),
  ('CDAT', 'ESTG'),
  ('CDAT', 'BD1'),
  ('ISW2', 'ISW1'),
  ('IOT', 'INFT'),
  ('CIBS', 'INFT'),
  ('IOP1', 'ALIN'),
  ('IOP1', 'ESTG'),
  ('PIS1', 'ISW2'),
  ('DSIS', 'TSOR'),
  ('DSIS', 'EDIF'),
  ('IOP2', 'IOP1'),
  ('PIS2', 'PIS1'),
  ('PRAC', 'PIS2');

-- Estudiante de ejemplo: reemplázalo con tus datos o con la exportación de la app
INSERT INTO estudiante VALUES ('20221045', 'José Elías Cruz', 1, 8, '2026-2', 'ACTIVA');

INSERT INTO inscripcion (estudiante, asignatura, periodo, estado, nota, nombre_electiva) VALUES
  ('20221045', 'ALIN', '2022-1', 'aprobada', 3.4, NULL),
  ('20221045', 'CDIF', '2022-1', 'aprobada', 3.1, NULL),
  ('20221045', 'EXPR', '2022-1', 'aprobada', 4.4, NULL),
  ('20221045', 'FPRO', '2022-1', 'aprobada', 4, NULL),
  ('20221045', 'SEM1', '2022-1', 'aprobada', 4.3, NULL),
  ('20221045', 'CINT', '2026-2', 'cursando', NULL, NULL),
  ('20221045', 'DIUS', '2022-2', 'aprobada', 3.7, NULL),
  ('20221045', 'IDEN', '2022-2', 'aprobada', 4.6, NULL),
  ('20221045', 'LMEC', '2022-2', 'aprobada', 4.3, NULL),
  ('20221045', 'MECL', '2022-2', 'aprobada', 3.3, NULL),
  ('20221045', 'PCOM', '2022-2', 'aprobada', 4.6, NULL),
  ('20221045', 'TDRC', '2022-2', 'aprobada', 4.6, NULL),
  ('20221045', 'TDHU', '2022-2', 'aprobada', 4.3, NULL),
  ('20221045', 'CREA', '2023-1', 'aprobada', 4.5, NULL),
  ('20221045', 'ELEC', '2026-2', 'cursando', NULL, NULL),
  ('20221045', 'EDAA', '2023-1', 'aprobada', 4.4, NULL),
  ('20221045', 'LELE', '2026-2', 'cursando', NULL, NULL),
  ('20221045', 'MCOM', '2023-1', 'aprobada', 3.6, NULL),
  ('20221045', 'SEM2', '2023-1', 'aprobada', 4.4, NULL),
  ('20221045', 'BD1', '2023-2', 'aprobada', 4.5, NULL),
  ('20221045', 'DMUL', '2023-2', 'aprobada', 4.6, NULL),
  ('20221045', 'ESTG', '2023-2', 'aprobada', 3.5, NULL),
  ('20221045', 'IART', '2023-2', 'aprobada', 4.8, NULL),
  ('20221045', 'TMOV', '2023-2', 'aprobada', 4.6, NULL),
  ('20221045', 'ALRD', '2024-1', 'aprobada', 4.4, NULL),
  ('20221045', 'ASOF', '2024-1', 'aprobada', 3.9, NULL),
  ('20221045', 'BD2', '2024-1', 'aprobada', 4.5, NULL),
  ('20221045', 'EPR1', '2024-1', 'aprobada', 3.8, NULL),
  ('20221045', 'INFT', '2024-1', 'aprobada', 4.5, NULL),
  ('20221045', 'ISW1', '2024-1', 'aprobada', 4.7, NULL),
  ('20221045', 'CDAT', '2024-2', 'aprobada', 4.7, NULL),
  ('20221045', 'EPR2', '2024-2', 'aprobada', 4.1, NULL),
  ('20221045', 'ETIC', '2024-2', 'aprobada', 4.3, NULL),
  ('20221045', 'ISW2', '2024-2', 'aprobada', 4.4, NULL),
  ('20221045', 'IOT', '2024-2', 'aprobada', 4.7, NULL),
  ('20221045', 'TSOR', '2024-2', 'aprobada', 4.2, NULL),
  ('20221045', 'CIBS', '2026-2', 'cursando', NULL, NULL),
  ('20221045', 'ESH1', '2025-1', 'aprobada', 3.9, NULL),
  ('20221045', 'ECX1', '2026-2', 'cursando', NULL, 'Marca Personal Digital'),
  ('20221045', 'EPR3', '2026-2', 'cursando', NULL, 'Sistemas Inteligentes'),
  ('20221045', 'IOP1', '2026-2', 'cursando', NULL, NULL),
  ('20221045', 'PIS1', '2025-1', 'aprobada', 4.6, NULL),
  ('20221045', 'PIS2', '2026-2', 'cursando', NULL, NULL);

-- =====================================================================
-- Contexto académico en JSON: lo consume el flujo de n8n en cada mensaje
-- SELECT fn_contexto_estudiante('20221045');
-- =====================================================================
CREATE OR REPLACE FUNCTION fn_contexto_estudiante(p_codigo TEXT)
RETURNS JSON LANGUAGE sql STABLE AS $$
WITH e AS (
  SELECT es.*, p.nombre AS programa, p.creditos_total, p.max_creditos_semestre
  FROM estudiante es JOIN programa p ON p.id = es.programa_id
  WHERE es.codigo = p_codigo
),
ap AS (
  SELECT i.asignatura, i.nota, a.creditos, a.area
  FROM inscripcion i JOIN asignatura a ON a.codigo = i.asignatura
  WHERE i.estudiante = p_codigo AND i.estado = 'aprobada'
),
cu AS (
  SELECT a.* FROM inscripcion i JOIN asignatura a ON a.codigo = i.asignatura
  WHERE i.estudiante = p_codigo AND i.estado = 'cursando'
),
pend AS (
  SELECT a.* FROM asignatura a
  WHERE a.programa_id = (SELECT programa_id FROM e)
    AND a.codigo NOT IN (SELECT asignatura FROM ap)
    AND a.codigo NOT IN (SELECT codigo FROM cu)
)
SELECT json_build_object(
  'estudiante',        (SELECT nombre FROM e),
  'codigo',            p_codigo,
  'programa',          (SELECT programa FROM e),
  'periodo_actual',    (SELECT periodo_actual FROM e),
  'estado_matricula',  (SELECT estado_matricula FROM e),
  'creditos_aprobados',(SELECT COALESCE(SUM(creditos),0) FROM ap),
  'creditos_en_curso', (SELECT COALESCE(SUM(creditos),0) FROM cu),
  'creditos_total',    (SELECT creditos_total FROM e),
  'porcentaje_avance', (SELECT ROUND(100.0*COALESCE(SUM(creditos),0)/(SELECT creditos_total FROM e),1) FROM ap),
  'promedio',          (SELECT ROUND(SUM(nota*creditos)/NULLIF(SUM(creditos),0),2) FROM ap),
  'promedio_por_area', (SELECT json_object_agg(area, prom) FROM (SELECT area, ROUND(SUM(nota*creditos)/SUM(creditos),2) prom FROM ap GROUP BY area) t),
  'cursando',          (SELECT json_agg(json_build_object('codigo',codigo,'nombre',nombre,'creditos',creditos)) FROM cu),
  'pendientes',        (SELECT json_agg(json_build_object(
                          'codigo', p.codigo, 'nombre', p.nombre, 'semestre_plan', p.semestre, 'creditos', p.creditos,
                          'prerrequisitos_faltantes', (SELECT json_agg(r.requiere) FROM prerrequisito r
                                                       WHERE r.asignatura = p.codigo AND r.requiere NOT IN (SELECT asignatura FROM ap))
                        ) ORDER BY p.semestre) FROM pend p),
  'notas_bajas',       (SELECT json_agg(json_build_object('asignatura', a.nombre, 'nota', ap.nota))
                        FROM ap JOIN asignatura a ON a.codigo = ap.asignatura WHERE ap.nota < 3.3)
);
$$;

-- Vista rápida de avance por estudiante (útil para dashboards)
CREATE OR REPLACE VIEW v_avance AS
SELECT e.codigo, e.nombre, e.periodo_actual,
       COALESCE(SUM(a.creditos) FILTER (WHERE i.estado='aprobada'),0) AS creditos_aprobados,
       COALESCE(SUM(a.creditos) FILTER (WHERE i.estado='cursando'),0) AS creditos_en_curso,
       p.creditos_total,
       ROUND(SUM(i.nota*a.creditos) FILTER (WHERE i.estado='aprobada') / NULLIF(SUM(a.creditos) FILTER (WHERE i.estado='aprobada'),0),2) AS promedio
FROM estudiante e
JOIN programa p ON p.id = e.programa_id
LEFT JOIN inscripcion i ON i.estudiante = e.codigo
LEFT JOIN asignatura a ON a.codigo = i.asignatura
GROUP BY e.codigo, e.nombre, e.periodo_actual, p.creditos_total;


-- =====================================================================
-- SEMESTRE ACTUAL · notas por evaluación (escala 0,0 – 5,0) y tareas
-- La app lee y escribe estas tablas por la API REST de Supabase (PostgREST).
-- =====================================================================
DROP TABLE IF EXISTS tarea, evaluacion CASCADE;

CREATE TABLE evaluacion (
  id          TEXT PRIMARY KEY,
  estudiante  TEXT NOT NULL,
  asignatura  TEXT NOT NULL REFERENCES asignatura(codigo),
  nombre      TEXT NOT NULL,
  tipo        TEXT NOT NULL DEFAULT 'parcial',        -- parcial | quiz | taller | laboratorio | proyecto | examen | exposicion | informe | otro
  corte       INT  NOT NULL CHECK (corte BETWEEN 1 AND 3),
  peso        NUMERIC(5,2) NOT NULL CHECK (peso >= 0 AND peso <= 100),   -- % de la nota final
  nota        NUMERIC(3,1) CHECK (nota >= 0 AND nota <= 5),               -- NULL = aún sin calificar
  fecha       DATE NOT NULL
);
CREATE INDEX ON evaluacion (estudiante, asignatura);

CREATE TABLE tarea (
  id            TEXT PRIMARY KEY,
  estudiante    TEXT NOT NULL,
  asignatura    TEXT NOT NULL REFERENCES asignatura(codigo),
  titulo        TEXT NOT NULL,
  descripcion   TEXT,
  fecha_entrega DATE NOT NULL,
  estado        TEXT NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente','en_progreso','entregada','calificada')),
  progreso      INT  NOT NULL DEFAULT 0 CHECK (progreso BETWEEN 0 AND 100),
  nota          NUMERIC(3,1) CHECK (nota >= 0 AND nota <= 5),
  evaluacion_id TEXT REFERENCES evaluacion(id) ON DELETE SET NULL
);
CREATE INDEX ON tarea (estudiante, fecha_entrega);

-- Notas del semestre: acumulado, nota actual, nota necesaria para 3,0 y estado
CREATE OR REPLACE VIEW v_notas_semestre AS
SELECT e.estudiante, e.asignatura, a.nombre AS asignatura_nombre, a.creditos,
       SUM(e.peso)                                                        AS peso_total,
       COALESCE(SUM(e.peso) FILTER (WHERE e.nota IS NOT NULL), 0)        AS peso_evaluado,
       ROUND(COALESCE(SUM(e.nota * e.peso / 100), 0), 2)                 AS acumulado,
       ROUND(SUM(e.nota * e.peso) FILTER (WHERE e.nota IS NOT NULL)
             / NULLIF(SUM(e.peso) FILTER (WHERE e.nota IS NOT NULL), 0), 2) AS nota_actual,
       CASE WHEN SUM(e.peso) - COALESCE(SUM(e.peso) FILTER (WHERE e.nota IS NOT NULL), 0) > 0
            THEN ROUND((3.0 - COALESCE(SUM(e.nota * e.peso / 100), 0))
                 / ((SUM(e.peso) - COALESCE(SUM(e.peso) FILTER (WHERE e.nota IS NOT NULL), 0)) / 100), 2) END AS nota_necesaria,
       CASE
         WHEN COUNT(*) = COUNT(e.nota) THEN CASE WHEN ROUND(SUM(e.nota * e.peso) / SUM(e.peso), 1) >= 3.0 THEN 'APROBADA' ELSE 'REPROBADA' END
         WHEN COALESCE(SUM(e.nota * e.peso / 100), 0) >= 3.0 THEN 'APROBADA ASEGURADA'
         WHEN COALESCE(SUM(e.nota * e.peso / 100), 0) + (SUM(e.peso) - COALESCE(SUM(e.peso) FILTER (WHERE e.nota IS NOT NULL), 0)) / 100 * 5 < 3.0 THEN 'PERDIDA'
         WHEN SUM(e.nota * e.peso) FILTER (WHERE e.nota IS NOT NULL) / NULLIF(SUM(e.peso) FILTER (WHERE e.nota IS NOT NULL), 0) < 3.0 THEN 'EN RIESGO'
         ELSE 'APROBANDO' END AS estado
FROM evaluacion e JOIN asignatura a ON a.codigo = e.asignatura
GROUP BY e.estudiante, e.asignatura, a.nombre, a.creditos;

-- Tareas con categoría calculada
CREATE OR REPLACE VIEW v_tareas AS
SELECT t.*, a.nombre AS asignatura_nombre, (t.fecha_entrega - CURRENT_DATE) AS dias_para_entrega,
       CASE WHEN t.estado IN ('entregada','calificada') THEN 'entregada'
            WHEN t.fecha_entrega < CURRENT_DATE THEN 'vencida'
            WHEN t.estado = 'en_progreso' THEN 'incompleta'
            ELSE 'por hacer' END AS categoria
FROM tarea t JOIN asignatura a ON a.codigo = t.asignatura;

-- Acceso desde la app con la anon key (proyecto de demostración académica).
-- En producción se reemplaza por autenticación (Supabase Auth) y políticas por estudiante.
ALTER TABLE evaluacion ENABLE ROW LEVEL SECURITY;
ALTER TABLE tarea      ENABLE ROW LEVEL SECURITY;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
    EXECUTE 'CREATE POLICY demo_evaluacion ON evaluacion FOR ALL TO anon USING (true) WITH CHECK (true)';
    EXECUTE 'CREATE POLICY demo_tarea ON tarea FOR ALL TO anon USING (true) WITH CHECK (true)';
    EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON evaluacion, tarea TO anon';
    EXECUTE 'GRANT SELECT ON v_notas_semestre, v_tareas, asignatura TO anon';
  END IF;
END $$;

-- Datos de ejemplo del semestre (fechas relativas a hoy)
INSERT INTO evaluacion (id, estudiante, asignatura, nombre, tipo, corte, peso, nota, fecha) VALUES
  ('ev_001', '20221045', 'CINT', 'Parcial 1', 'parcial', 1, 20, 2.6, CURRENT_DATE + -70),
  ('ev_002', '20221045', 'CINT', 'Quiz 1: antiderivadas', 'quiz', 1, 10, 3.4, CURRENT_DATE + -63),
  ('ev_003', '20221045', 'CINT', 'Parcial 2', 'parcial', 2, 20, 2.8, CURRENT_DATE + -35),
  ('ev_004', '20221045', 'CINT', 'Taller: integración por partes', 'taller', 2, 10, 3.6, CURRENT_DATE + -28),
  ('ev_005', '20221045', 'CINT', 'Proyecto integrador (energía fotovoltaica)', 'proyecto', 3, 20, NULL, CURRENT_DATE + 6),
  ('ev_006', '20221045', 'CINT', 'Examen final', 'examen', 3, 20, NULL, CURRENT_DATE + 12),
  ('ev_007', '20221045', 'ELEC', 'Parcial 1', 'parcial', 1, 25, 3.5, CURRENT_DATE + -68),
  ('ev_008', '20221045', 'ELEC', 'Quiz: ley de Gauss', 'quiz', 1, 5, 3.8, CURRENT_DATE + -60),
  ('ev_009', '20221045', 'ELEC', 'Parcial 2', 'parcial', 2, 25, 3.2, CURRENT_DATE + -33),
  ('ev_010', '20221045', 'ELEC', 'Taller: circuitos RC', 'taller', 2, 5, 4, CURRENT_DATE + -26),
  ('ev_011', '20221045', 'ELEC', 'Examen final', 'examen', 3, 40, NULL, CURRENT_DATE + 13),
  ('ev_012', '20221045', 'LELE', 'Informe 1: ley de Ohm', 'informe', 1, 25, 4.2, CURRENT_DATE + -65),
  ('ev_013', '20221045', 'LELE', 'Informe 2: capacitores', 'informe', 2, 25, 4, CURRENT_DATE + -38),
  ('ev_014', '20221045', 'LELE', 'Informe 3: campo magnético', 'informe', 2, 25, 4.5, CURRENT_DATE + -20),
  ('ev_015', '20221045', 'LELE', 'Informe 4: ley de Faraday', 'informe', 3, 25, NULL, CURRENT_DATE + 2),
  ('ev_016', '20221045', 'IOP1', 'Parcial 1: programación lineal', 'parcial', 1, 20, 4, CURRENT_DATE + -66),
  ('ev_017', '20221045', 'IOP1', 'Taller: método Simplex', 'taller', 1, 10, 4.3, CURRENT_DATE + -58),
  ('ev_018', '20221045', 'IOP1', 'Parcial 2: transporte y asignación', 'parcial', 2, 20, 3.7, CURRENT_DATE + -31),
  ('ev_019', '20221045', 'IOP1', 'Quiz: dualidad', 'quiz', 2, 10, 4.5, CURRENT_DATE + -24),
  ('ev_020', '20221045', 'IOP1', 'Trabajo de investigación: modelos de inventarios', 'proyecto', 3, 20, NULL, CURRENT_DATE + 3),
  ('ev_021', '20221045', 'IOP1', 'Examen final', 'examen', 3, 20, NULL, CURRENT_DATE + 11),
  ('ev_022', '20221045', 'PIS2', 'Avance 1: diseño del prototipo', 'proyecto', 1, 30, 4.5, CURRENT_DATE + -60),
  ('ev_023', '20221045', 'PIS2', 'Avance 2: prototipo funcional', 'proyecto', 2, 30, 4.3, CURRENT_DATE + -25),
  ('ev_024', '20221045', 'PIS2', 'Sustentación final ante jurado', 'exposicion', 3, 40, NULL, CURRENT_DATE + 6),
  ('ev_025', '20221045', 'CIBS', 'Parcial 1', 'parcial', 1, 20, 3.9, CURRENT_DATE + -64),
  ('ev_026', '20221045', 'CIBS', 'Laboratorio TryHackMe', 'laboratorio', 1, 10, 4.6, CURRENT_DATE + -55),
  ('ev_027', '20221045', 'CIBS', 'Parcial 2', 'parcial', 2, 20, 4.1, CURRENT_DATE + -30),
  ('ev_028', '20221045', 'CIBS', 'Informe de riesgos MAGERIT', 'informe', 2, 10, 4.4, CURRENT_DATE + -21),
  ('ev_029', '20221045', 'CIBS', 'Hackathon CyberRisk 2.0', 'proyecto', 3, 20, NULL, CURRENT_DATE + 4),
  ('ev_030', '20221045', 'CIBS', 'Examen final', 'examen', 3, 20, NULL, CURRENT_DATE + 10),
  ('ev_031', '20221045', 'ECX1', 'Perfil profesional en LinkedIn', 'taller', 1, 20, 4.8, CURRENT_DATE + -62),
  ('ev_032', '20221045', 'ECX1', 'Portafolio digital', 'proyecto', 2, 25, 4.5, CURRENT_DATE + -29),
  ('ev_033', '20221045', 'ECX1', 'Pitch personal (video)', 'exposicion', 2, 15, 4.2, CURRENT_DATE + -18),
  ('ev_034', '20221045', 'ECX1', 'Proyecto final: estrategia de marca personal', 'proyecto', 3, 40, NULL, CURRENT_DATE + 8),
  ('ev_035', '20221045', 'EPR3', 'Taller: aprendizaje supervisado', 'taller', 1, 15, 4.2, CURRENT_DATE + -61),
  ('ev_036', '20221045', 'EPR3', 'Parcial 1', 'parcial', 1, 20, 3.6, CURRENT_DATE + -52),
  ('ev_037', '20221045', 'EPR3', 'Parcial 2: redes neuronales', 'parcial', 2, 15, 3.9, CURRENT_DATE + -27),
  ('ev_038', '20221045', 'EPR3', 'Proyecto: detector de somnolencia con Roboflow', 'proyecto', 3, 30, NULL, CURRENT_DATE + 5),
  ('ev_039', '20221045', 'EPR3', 'Examen final', 'examen', 3, 20, NULL, CURRENT_DATE + 13);

INSERT INTO tarea (id, estudiante, asignatura, titulo, descripcion, fecha_entrega, estado, progreso, nota, evaluacion_id) VALUES
  ('tk_001', '20221045', 'CINT', 'Proyecto integrador · Fase 3 (energía fotovoltaica)', 'Confirmar con el profesor si se entrega póster o documento escrito.', CURRENT_DATE + 6, 'en_progreso', 40, NULL, 'ev_005'),
  ('tk_002', '20221045', 'CINT', 'Taller 5: volúmenes de sólidos de revolución', 'Ejercicios 1 a 12 de la guía.', CURRENT_DATE + -1, 'pendiente', 0, NULL, NULL),
  ('tk_003', '20221045', 'CINT', 'Guía de repaso para el examen final', 'Integración por partes, fracciones parciales e impropias.', CURRENT_DATE + 10, 'pendiente', 0, NULL, NULL),
  ('tk_004', '20221045', 'LELE', 'Informe 4: ley de Faraday', 'Falta análisis de error y conclusiones.', CURRENT_DATE + 2, 'en_progreso', 60, NULL, 'ev_015'),
  ('tk_005', '20221045', 'ELEC', 'Taller: circuitos RC', NULL, CURRENT_DATE + -26, 'calificada', 100, 4, NULL),
  ('tk_006', '20221045', 'ELEC', 'Ejercicios de inducción (cap. 30)', 'Preparación para el final.', CURRENT_DATE + 7, 'pendiente', 0, NULL, NULL),
  ('tk_007', '20221045', 'IOP1', 'Trabajo de investigación: modelos de inventarios (EOQ, Silver-Meal) · LaTeX IEEE', 'En Overleaf. Faltan la sección de Silver-Meal y las referencias.', CURRENT_DATE + 3, 'en_progreso', 55, NULL, 'ev_020'),
  ('tk_008', '20221045', 'PIS2', 'Presentación del dispositivo de hardware', 'Sustentación ante jurado.', CURRENT_DATE + 6, 'en_progreso', 80, NULL, 'ev_024'),
  ('tk_009', '20221045', 'PIS2', 'Documento final y póster', 'Formato institucional.', CURRENT_DATE + 5, 'en_progreso', 70, NULL, NULL),
  ('tk_010', '20221045', 'PIS2', 'Ensayo de la sustentación', 'Cronometrar 15 minutos.', CURRENT_DATE + 4, 'pendiente', 0, NULL, NULL),
  ('tk_011', '20221045', 'CIBS', 'Hackathon CyberRisk 2.0 · Reto 1: The Marketplace (TryHackMe)', 'Rol: líder de análisis de riesgos. Parte Red Team.', CURRENT_DATE + 4, 'en_progreso', 30, NULL, 'ev_029'),
  ('tk_012', '20221045', 'CIBS', 'Matriz de riesgos MAGERIT del reto', 'Activos, amenazas, impacto y probabilidad.', CURRENT_DATE + 4, 'pendiente', 0, NULL, NULL),
  ('tk_013', '20221045', 'EPR3', 'Dataset etiquetado en Roboflow', 'Faltan ~80 imágenes por etiquetar (ojos cerrados / bostezo).', CURRENT_DATE + -2, 'en_progreso', 70, NULL, NULL),
  ('tk_014', '20221045', 'EPR3', 'Proyecto: detector de somnolencia con Roboflow + Camo', 'Entrenar el modelo y probar en tiempo real con la cámara del celular.', CURRENT_DATE + 5, 'en_progreso', 45, NULL, 'ev_038'),
  ('tk_015', '20221045', 'ECX1', 'Proyecto final: estrategia de marca personal', 'Plan de contenidos de 4 semanas y métricas.', CURRENT_DATE + 8, 'pendiente', 0, NULL, 'ev_034'),
  ('tk_016', '20221045', 'ECX1', 'Publicar 3 posts en LinkedIn', NULL, CURRENT_DATE + -12, 'calificada', 100, 4.6, NULL);

-- Consultas útiles:
--   SELECT * FROM v_notas_semestre WHERE estudiante = '20221045';
--   SELECT titulo, asignatura_nombre, fecha_entrega, categoria FROM v_tareas WHERE estudiante = '20221045' ORDER BY fecha_entrega;

-- Nota: n8n crea solas las tablas n8n_chat_histories (memoria) y n8n_vectors (RAG)
-- la primera vez que corren los nodos Postgres Chat Memory y PGVector Store.
