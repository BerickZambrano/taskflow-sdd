# Plan 003 — Etiquetas, racha, tiempo y vencidas

Define CÓMO se implementa la spec 003 sobre la API (spec 001) y la web (spec 002).
Un solo usuario → etiquetas, tiempo y estadísticas globales, sin propietario.

## 1. Modelo de datos (migración Alembic)

- **Tag**: `id` (UUID PK), `name` (String 50, único **insensible a mayúsculas**),
  `color` (String 20, hex), `created_at`.
- **task_tags** (N:N): `task_id` FK (CASCADE), `tag_id` FK (CASCADE),
  única `(task_id, tag_id)`.
- **TimeEntry**: `id` (UUID PK), `task_id` FK (CASCADE, nullable), `minutes` (int),
  `entry_date` (Date), `created_at`.
- **Task** (+ columna): `completed_at` (DateTime tz, nullable). Se setea al pasar a
  `done`; se limpia si ya no está `done`.

Índice funcional único para `name` de etiquetas: `lower(name)` (mismo patrón que proyectos).

## 2. Lógica de negocio

- **Color autoasignado**: paleta fija de hex; `paleta[count % len]` al crear.
- **completed_at**: en `TaskService.update`, al aplicar `status=done` → `now`; si el estado
  ya no es `done` → `None`.
- **Racha** (pseudocódigo):
  ```
  dias = { date(completed_at) | tarea.completed_at != null and date <= hoy }
  streak = 0
  d = hoy
  SI hoy no está en dias: d = hoy - 1   # tolerancia "aún no estudio hoy"
  MIENTRAS d in dias: streak += 1; d -= 1
  ```

## 3. Contrato de la API

### Etiquetas
| Método y ruta | Cuerpo | Éxito | Errores | RF |
|---|---|---|---|---|
| GET `/tags` | — | `200` lista | — | RF-3.2 |
| POST `/tags` | `{name}` | `201` | `409` duplicado; `422` | RF-3.1 |
| DELETE `/tags/{id}` | — | `204` | `404` | RF-3.3 |
| POST `/tasks/{id}/tags` | `{tag_id}` | `200` tarea | `404` tarea/etiqueta | RF-3.4 |
| DELETE `/tasks/{id}/tags/{tag_id}` | — | `200` tarea | `404` | RF-3.5 |

`TaskOut` incluye `tags: TagOut[]`. El listado de tareas acepta `tag_id` como filtro (RF-3.6).

### Tiempo / estadísticas
| Método y ruta | Cuerpo | Éxito | RF |
|---|---|---|---|
| POST `/time-entries` | `{task_id?, minutes, entry_date?}` | `201` | RF-3.8 |
| GET `/time-entries?from=&to=` | — | `200` lista | RF-3.8 |
| GET `/stats` | — | `200` `{streak, days_studied, tasks_completed, minutes_total, minutes_by_day, minutes_by_tag, minutes_by_project}` | RF-3.9–3.11 |

### Vencidas
Sin endpoint nuevo: se deriva en el cliente de `due_date` + `status`/`completed_at` (RF-3.7).

## 4. Decisiones técnicas (y alternativa descartada)

| Decisión | Justificación | Alternativa descartada |
|---|---|---|
| `completed_at` en Task | Fuente simple y fiable para la racha | Tabla de eventos — más compleja |
| Color autoasignado por paleta | Cumple RF-3.1 sin UI extra | Color manual — requiere más UI |
| Racha calculada en consulta | Simple, sin jobs/cache | Cache previa — innecesaria |
| `TimeEntry` con `task_id` | Vincula tiempo a tarea/proyecto/etiqueta | Campo texto libre — pierde agrupación |

## 5. Estrategia de tests

- **Backend (pytest)**: repo (tags únicos, task_tags sin duplicados, time entry),
  servicio (color, completed_at, bloqueos), stats/racha (huecos, hoy sin actividad,
  sin completadas), rutas (códigos y mensajes en español).
- **Frontend (Vitest)**: filtro por etiqueta, detección vencida/próxima, panel de estadísticas.
