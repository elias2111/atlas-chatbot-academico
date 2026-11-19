# Evidencia de recuperación del RAG

Generado con `python rag/rag_local.py eval` el 19/11/2026 00:05.

## Corpus e índice

- Documentos: Guía de éxito académico para Ingeniería de Sistemas, Plan de estudios de Ingeniería de Sistemas (UNAB) · 9 semestres, 151 créditos, Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave
- Fragmentos: **35** · tamaño promedio 512 caracteres (mín. 92, máx. 988)
- Parámetros: `chunk_size = 1000`, `chunk_overlap = 150`, separadores ['\n\n', '\n- ', '. ', ' ']
- Recuperador evaluado: BM25 (el mismo que corre en la app). En n8n se usa búsqueda semántica con `text-embedding-3-small` + pgvector (top-k 4).

## Resultados (12 consultas)

| Métrica | Valor |
|---|---|
| Acierto en el 1.er resultado (precisión@1) | **10/12 = 83%** |
| Acierto entre los 3 primeros (recall@3) | **12/12 = 100%** |

| Consulta | Sección esperada | 1.er resultado | Score | @1 | @3 |
|---|---|---|---|---|---|
| ¿Con qué nota se aprueba una materia? | Escala de calificaciones | Cómo calcula ATLAS la nota necesaria para aprobar | 5.667 | ✖ | ✔ |
| Saqué 2,6 de definitiva, ¿puedo habilitar? | Habilitaciones | Habilitaciones (Arts. 47 y 48) | 9.28 | ✔ | ✔ |
| ¿Cuántas veces puedo cancelar la misma materia? | Cancelación | Cancelación de cursos y del período (Art. 13) | 8.197 | ✔ | ✔ |
| ¿Qué pasa si tengo muchas fallas en una clase? | Asistencia | Asistencia y pérdida por fallas (Art. 46) | 4.514 | ✔ | ✔ |
| ¿Qué requisitos necesito para graduarme? | Requisitos de grado | Requisitos de grado (Arts. 7, 67 y 68) | 4.079 | ✔ | ✔ |
| ¿Qué es la prueba académica y cuándo pierdo el cupo? | prueba académica | Estado académico condicional, prueba académica y pérdida de cupo (Arts. 10, 11, 12, 84 y 85) | 9.188 | ✔ | ✔ |
| ¿La nota definitiva se redondea? | Redondeo | Redondeo de la nota definitiva (Arts. 39 y 40) | 6.55 | ✔ | ✔ |
| No pude presentar el parcial porque estaba enfermo, ¿qué hago? | supletorios | Exámenes supletorios (Art. 45) | 3.688 | ✔ | ✔ |
| ¿Qué prerrequisitos tiene Dinámica de sistemas? | Octavo semestre | Sexto semestre (17 créditos) | 5.428 | ✖ | ✔ |
| ¿Qué técnicas de estudio funcionan mejor según la evidencia? | Técnicas de estudio | Técnicas de estudio con mayor evidencia | 10.034 | ✔ | ✔ |
| ¿Cómo se calcula la nota que necesito para pasar? | nota necesaria | Cómo calcula ATLAS la nota necesaria para aprobar | 6.533 | ✔ | ✔ |
| ¿Qué es la educación de precisión? | Educación de precisión | Educación de precisión: qué es y cómo la aplica ATLAS | 7.389 | ✔ | ✔ |

## Fragmentos recuperados por consulta

### ¿Con qué nota se aprueba una materia?
1. **Guía de éxito académico para Ingeniería de Sistemas › Cómo calcula ATLAS la nota necesaria para aprobar** (score 5.667)  
   > Cada evaluación tiene un peso en porcentaje. El acumulado es la suma de nota × peso de las evaluaciones ya calificadas. La nota necesaria es (3,0 − acumulado) dividido entre el peso que falta por evaluar. Si el acumulado ya es 3,0 o más, la materia está aproba…
2. **Guía de éxito académico para Ingeniería de Sistemas › Educación de precisión: qué es y cómo la aplica ATLAS** (score 3.404)  
   > La educación de precisión adapta el apoyo a cada estudiante a partir de sus datos, de forma parecida a como la medicina de precisión adapta un tratamiento: diagnosticar, predecir, intervenir y prevenir (Yang, 2021). Una revisión de 40 estudios empíricos encont…
3. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Escala de calificaciones y nota aprobatoria (Arts. 37 y 38)** (score 2.636)  
   > Las pruebas cuantitativas se califican de 0,0 a 5,0 y la nota mínima aprobatoria es 3,0. Una prueba que no se presenta se califica con 0,0. Las pruebas cualitativas, los cursos instrumentales y los de Bienestar Universitario se califican como aprobado o reprob…

### Saqué 2,6 de definitiva, ¿puedo habilitar?
1. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Habilitaciones (Arts. 47 y 48)** (score 9.28)  
   > Un curso reprobado se puede habilitar una sola vez si la calificación final es de al menos 2,5 y el programa lo define como habilitable. Se pueden habilitar como máximo dos cursos por período. No se habilitan seminarios, talleres, prácticas, cursos instrumenta…
2. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Redondeo de la nota definitiva (Arts. 39 y 40)** (score 4.168)  
   > La nota final de un curso se expresa en unidades y décimas sin aproximar: las cifras decimales adicionales se eliminan. Por ejemplo, una definitiva calculada de 2,96 queda en 2,9 y no se sube a 3,0. Los promedios del período (PPA) y el promedio general acumula…
3. **Guía de éxito académico para Ingeniería de Sistemas › Cómo calcula ATLAS la nota necesaria para aprobar** (score 3.433)  
   > Cada evaluación tiene un peso en porcentaje. El acumulado es la suma de nota × peso de las evaluaciones ya calificadas. La nota necesaria es (3,0 − acumulado) dividido entre el peso que falta por evaluar. Si el acumulado ya es 3,0 o más, la materia está aproba…

### ¿Cuántas veces puedo cancelar la misma materia?
1. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Cancelación de cursos y del período (Art. 13)** (score 8.197)  
   > La cancelación ordinaria se solicita dentro de las fechas del cronograma del programa. La cancelación extraordinaria solo procede por fuerza mayor o caso fortuito comprobados, hasta el día hábil siguiente a la terminación de clases; el bajo rendimiento y el ex…
2. **Guía de éxito académico para Ingeniería de Sistemas › Técnicas de estudio con mayor evidencia** (score 4.732)  
   > Una revisión de diez técnicas de estudio comunes calificó dos como de alta utilidad: la práctica de recuperación (autoevaluarse con preguntas, ejercicios o tarjetas) y la práctica distribuida (repartir el estudio en varias sesiones en lugar de concentrarlo ant…
3. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Práctica académica (Arts. 56 y 60)** (score 3.557)  
   > La práctica es un curso del plan de estudios. Para inscribirla se deben cumplir los prerrequisitos que fija el programa. El Art. 60 regula la cancelación de la práctica.…

### ¿Qué pasa si tengo muchas fallas en una clase?
1. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Asistencia y pérdida por fallas (Art. 46)** (score 4.514)  
   > Si al terminar el curso la inasistencia es del 20 % o más de las horas exigidas, el último registro de notas se califica con 0,0 (no aplica a programas virtuales). Presentar una justa causa no cambia el conteo de inasistencias.…
2. **Guía de éxito académico para Ingeniería de Sistemas › Gestión de la carga académica** (score 3.153)  
   > Por cada crédito se recomiendan unas dos horas de trabajo independiente por semana además de la clase. Con cargas superiores a 18 créditos conviene bloquear las horas en el calendario y revisar cada semana qué asignatura se atrasó. Si una materia baja de 3,0 e…
3. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Cancelación de cursos y del período (Art. 13)** (score 2.611)  
   > La cancelación ordinaria se solicita dentro de las fechas del cronograma del programa. La cancelación extraordinaria solo procede por fuerza mayor o caso fortuito comprobados, hasta el día hábil siguiente a la terminación de clases; el bajo rendimiento y el ex…

### ¿Qué requisitos necesito para graduarme?
1. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Requisitos de grado (Arts. 7, 67 y 68)** (score 4.079)  
   > Para obtener el título se debe, entre otros requisitos: acreditar el nivel de inglés exigido en el currículo, certificado por el Departamento de Lenguas o con una prueba internacional avalada por él; tener un PGA igual o superior a 3,20 en el programa; present…
2. **Guía de éxito académico para Ingeniería de Sistemas › Autoaprendizaje** (score 2.655)  
   > El autoaprendizaje funciona mejor con metas concretas y retroalimentación frecuente. Recursos recomendados para Ingeniería de Sistemas: documentación oficial (PostgreSQL, n8n, Python), cursos abiertos como Khan Academy para matemáticas y Cisco Networking Acade…
3. **Guía de éxito académico para Ingeniería de Sistemas › Educación de precisión: qué es y cómo la aplica ATLAS** (score 1.946)  
   > La educación de precisión adapta el apoyo a cada estudiante a partir de sus datos, de forma parecida a como la medicina de precisión adapta un tratamiento: diagnosticar, predecir, intervenir y prevenir (Yang, 2021). Una revisión de 40 estudios empíricos encont…

### ¿Qué es la prueba académica y cuándo pierdo el cupo?
1. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Estado académico condicional, prueba académica y pérdida de cupo (Arts. 10, 11, 12, 84 y 85)** (score 9.188)  
   > Un estudiante queda en estado académico condicional cuando su PGA está entre 3,00 y 3,20; en ese estado puede matricular como máximo tres cursos en el período siguiente (Art. 84). Entra en prueba académica si por segunda vez consecutiva su PGA queda entre 3,00…
2. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Práctica académica (Arts. 56 y 60)** (score 3.268)  
   > La práctica es un curso del plan de estudios. Para inscribirla se deben cumplir los prerrequisitos que fija el programa. El Art. 60 regula la cancelación de la práctica.…
3. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Requisitos de grado (Arts. 7, 67 y 68)** (score 3.06)  
   > Para obtener el título se debe, entre otros requisitos: acreditar el nivel de inglés exigido en el currículo, certificado por el Departamento de Lenguas o con una prueba internacional avalada por él; tener un PGA igual o superior a 3,20 en el programa; present…

### ¿La nota definitiva se redondea?
1. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Redondeo de la nota definitiva (Arts. 39 y 40)** (score 6.55)  
   > La nota final de un curso se expresa en unidades y décimas sin aproximar: las cifras decimales adicionales se eliminan. Por ejemplo, una definitiva calculada de 2,96 queda en 2,9 y no se sube a 3,0. Los promedios del período (PPA) y el promedio general acumula…
2. **Guía de éxito académico para Ingeniería de Sistemas › Cómo calcula ATLAS la nota necesaria para aprobar** (score 6.038)  
   > Cada evaluación tiene un peso en porcentaje. El acumulado es la suma de nota × peso de las evaluaciones ya calificadas. La nota necesaria es (3,0 − acumulado) dividido entre el peso que falta por evaluar. Si el acumulado ya es 3,0 o más, la materia está aproba…
3. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Habilitaciones (Arts. 47 y 48)** (score 4.364)  
   > Un curso reprobado se puede habilitar una sola vez si la calificación final es de al menos 2,5 y el programa lo define como habilitable. Se pueden habilitar como máximo dos cursos por período. No se habilitan seminarios, talleres, prácticas, cursos instrumenta…

### No pude presentar el parcial porque estaba enfermo, ¿qué hago?
1. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Exámenes supletorios (Art. 45)** (score 3.688)  
   > Quien no presenta una prueba por una justa causa puede pedir un examen supletorio una sola vez por prueba. La solicitud se hace dentro de los cinco días hábiles siguientes a la fecha en que estaba programada la prueba y debe llevar el soporte de la justa causa…
2. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Cómo se evalúa un curso (Arts. 34, 35 y 44)** (score 3.463)  
   > La evaluación tiene tres momentos: diagnóstico, proceso y resultados; solo el de resultados lleva calificación numérica. Al inicio del curso el profesor define en la guía de cátedra las pruebas, los criterios y el porcentaje de cada una. Los parciales o previo…
3. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Asistencia y pérdida por fallas (Art. 46)** (score 2.981)  
   > Si al terminar el curso la inasistencia es del 20 % o más de las horas exigidas, el último registro de notas se califica con 0,0 (no aplica a programas virtuales). Presentar una justa causa no cambia el conteo de inasistencias.…

### ¿Qué prerrequisitos tiene Dinámica de sistemas?
1. **Plan de estudios de Ingeniería de Sistemas (UNAB) · 9 semestres, 151 créditos › Sexto semestre (17 créditos)** (score 5.428)  
   > - Ciencias de datos (CDAT): 3 créditos, área Sistemas. Prerrequisitos: Estadística general, Base de datos I. Desbloquea: ninguna. - Electiva de profundización II (EPR2): 3 créditos, área Electivas. Prerrequisitos: ninguno. Desbloquea: ninguna. - Ética de la in…
2. **Plan de estudios de Ingeniería de Sistemas (UNAB) · 9 semestres, 151 créditos › Octavo semestre (16 créditos)** (score 5.405)  
   > - Dinámica de sistemas (DSIS): 3 créditos, área Sistemas. Prerrequisitos: Teoría de sistemas y organizaciones, Ecuaciones diferenciales. Desbloquea: ninguna. - Electiva sociohumanística II (ESH2): 3 créditos, área Electivas. Prerrequisitos: ninguno. Desbloquea…
3. **Plan de estudios de Ingeniería de Sistemas (UNAB) · 9 semestres, 151 créditos › Cuarto semestre (18 créditos)** (score 5.028)  
   > - Base de datos I (BD1): 3 créditos, área Sistemas. Prerrequisitos: Estructura de datos y análisis de algoritmos. Desbloquea: Base de datos II, Ingeniería de software I, Ciencias de datos. - Desarrollo multimedia (DMUL): 3 créditos, área Sistemas. Prerrequisit…

### ¿Qué técnicas de estudio funcionan mejor según la evidencia?
1. **Guía de éxito académico para Ingeniería de Sistemas › Técnicas de estudio con mayor evidencia** (score 10.034)  
   > Una revisión de diez técnicas de estudio comunes calificó dos como de alta utilidad: la práctica de recuperación (autoevaluarse con preguntas, ejercicios o tarjetas) y la práctica distribuida (repartir el estudio en varias sesiones en lugar de concentrarlo ant…
2. **Guía de éxito académico para Ingeniería de Sistemas › Autoaprendizaje** (score 6.659)  
   > El autoaprendizaje funciona mejor con metas concretas y retroalimentación frecuente. Recursos recomendados para Ingeniería de Sistemas: documentación oficial (PostgreSQL, n8n, Python), cursos abiertos como Khan Academy para matemáticas y Cisco Networking Acade…
3. **Plan de estudios de Ingeniería de Sistemas (UNAB) · 9 semestres, 151 créditos › Plan de estudios de Ingeniería de Sistemas (UNAB) · 9 semestres, 151 créditos** (score 3.772)  
   > Fuente: plan de estudios oficial del programa (asignaturas y créditos por semestre). Los prerrequisitos no aparecen en el plan publicado; los que se indican aquí son la propuesta que usa ATLAS y deben confirmarse con la coordinación del programa.…

### ¿Cómo se calcula la nota que necesito para pasar?
1. **Guía de éxito académico para Ingeniería de Sistemas › Cómo calcula ATLAS la nota necesaria para aprobar** (score 6.533)  
   > Cada evaluación tiene un peso en porcentaje. El acumulado es la suma de nota × peso de las evaluaciones ya calificadas. La nota necesaria es (3,0 − acumulado) dividido entre el peso que falta por evaluar. Si el acumulado ya es 3,0 o más, la materia está aproba…
2. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Promedio general acumulado PGA (Art. 40)** (score 3.447)  
   > El PGA se calcula sumando cada calificación final multiplicada por los créditos del curso y dividiendo entre el total de créditos cursados. Es un promedio ponderado por créditos.…
3. **Reglamento Estudiantil de Pregrado UNAB (2019) · Normas académicas clave › Escala de calificaciones y nota aprobatoria (Arts. 37 y 38)** (score 2.636)  
   > Las pruebas cuantitativas se califican de 0,0 a 5,0 y la nota mínima aprobatoria es 3,0. Una prueba que no se presenta se califica con 0,0. Las pruebas cualitativas, los cursos instrumentales y los de Bienestar Universitario se califican como aprobado o reprob…

### ¿Qué es la educación de precisión?
1. **Guía de éxito académico para Ingeniería de Sistemas › Educación de precisión: qué es y cómo la aplica ATLAS** (score 7.389)  
   > La educación de precisión adapta el apoyo a cada estudiante a partir de sus datos, de forma parecida a como la medicina de precisión adapta un tratamiento: diagnosticar, predecir, intervenir y prevenir (Yang, 2021). Una revisión de 40 estudios empíricos encont…
2. **Guía de éxito académico para Ingeniería de Sistemas › Guía de éxito académico para Ingeniería de Sistemas** (score 6.087)  
   > Base pedagógica de las recomendaciones de ATLAS en tres líneas: educación de precisión, autoaprendizaje e investigación. Cada recomendación se apoya en evidencia publicada (ver Referencias).…
3. **Guía de éxito académico para Ingeniería de Sistemas › Referencias** (score 2.537)  
   > - Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J. y Willingham, D. T. (2013). Improving students' learning with effective learning techniques: Promising directions from cognitive and educational psychology. Psychological Science in the Public Interest…
