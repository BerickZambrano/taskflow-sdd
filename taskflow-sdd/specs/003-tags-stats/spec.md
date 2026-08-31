# Spec 003 — Etiquetas, racha, tiempo y vencidas

## Contexto y objetivo

TaskFlow (spec 001/002) gestiona proyectos y tareas. Esta spec amplía la herramienta
para el uso personal de proyectos y estudios: etiquetar tareas por materia/área, detectar
tareas vencidas o próximas a vencer, registrar tiempo de estudio y medir la constancia
(racha y estadísticas). El alcance es de **un solo usuario** (sin roles ni colaboración).

## Usuarios

- **Usuario**: organiza su trabajo y estudios en un solo espacio personal.

## Historias de usuario

- **US-1**: Como usuario, quiero etiquetar tareas por materia/área para agruparlas.
- **US-2**: Como usuario, quiero ver de un vistazo las tareas vencidas o próximas.
- **US-3**: Como usuario, quiero registrar el tiempo que dedico a cada tarea.
- **US-4**: Como usuario, quiero ver mi racha de estudio y estadísticas de constancia.

## Requisitos funcionales

### Etiquetas

- **RF-3.1** — Crear etiqueta. CUANDO el usuario crea una etiqueta con un nombre nuevo,
  ENTONCES el sistema DEBE crearla con un color asignado automáticamente. SI el nombre ya
  existe, ENTONCES el sistema DEBE rechazarla e informar en español.
- **RF-3.2** — Listar etiquetas. CUANDO el usuario consulta las etiquetas, ENTONCES el
  sistema DEBE devolverlas con su color.
- **RF-3.3** — Eliminar etiqueta. CUANDO el usuario elimina una etiqueta, ENTONCES el
  sistema DEBE eliminarla y desvincularla de todas las tareas.
- **RF-3.4** — Asignar etiqueta a tarea. CUANDO el usuario asigna una etiqueta, ENTONCES
  el sistema DEBE vincularla a la tarea (sin duplicados).
- **RF-3.5** — Quitar etiqueta de tarea. CUANDO el usuario quita una etiqueta, ENTONCES
  el sistema DEBE desvincularla de la tarea.
- **RF-3.6** — Etiquetas y filtro. CUANDO el sistema devuelve una tarea, ENTONCES DEBE
  incluir sus etiquetas. EL tablero DEBE permitir filtrar por etiqueta.

### Vencidas y recordatorios

- **RF-3.7** — Detección. CUANDO una tarea no está completada y su fecha límite es
  anterior a hoy, ENTONCES el sistema DEBE marcarla como "vencida". SI vence dentro de 3
  días, ENTONCES DEBE marcarla como "próxima". La interfaz DEBE mostrarlo claramente.

### Tiempo y racha

- **RF-3.8** — Registrar tiempo. CUANDO el usuario registra minutos para una tarea o una
  fecha, ENTONCES el sistema DEBE guardarlo.
- **RF-3.9** — Fecha de finalización. CUANDO una tarea pasa a `done`, ENTONCES el sistema
  DEBE registrar su fecha de finalización. SI deja de estar `done`, ENTONCES DEBE
  descartarla.
- **RF-3.10** — Racha. CUANDO se consultan las estadísticas, ENTONCES el sistema DEBE
  devolver los días consecutivos con al menos una tarea completada (hasta hoy).
- **RF-3.11** — Estadísticas. CUANDO se consultan las estadísticas, ENTONCES el sistema
  DEBE devolver días estudiados, tareas completadas, minutos totales y minutos agrupados
  por día, etiqueta y proyecto.

## Requisitos no funcionales

- **RNF-1** — Mensajes en español; código en inglés (constitución).
- **RNF-2** — Cambios de esquema mediante migraciones y reflejados en esta spec.
- **RNF-3** — Tests automatizados (pytest backend, Vitest frontend) para cada parte.
- **RNF-4** — Sin dependencias sin justificar.

## Casos límite

- Nombre de etiqueta duplicado (insensible a mayúsculas).
- Asignar dos veces la misma etiqueta a una tarea.
- Eliminar una etiqueta en uso.
- Tarea vencida vs. completada (no se marca vencida).
- Racha con hueco en el pasado, sin actividad hoy, o sin ninguna tarea completada.
- Registrar tiempo con minutos inválidos (≤ 0 o muy altos).

## Fuera de alcance

- Roles, permisos y colaboración (un solo usuario).
- Recordatorios por correo/notificaciones push.
- Métricas avanzadas (gráficos complejos, predicciones).

## Criterios de finalización

- Todos los RF-3.1 a RF-3.11 implementados y cubiertos por tests.
- `pytest -q` verde y `npm run build`/`npm test` verdes.
- Mensajes en español, código en inglés; migraciones aplicadas.
