# Tareas — Etiquetas, racha, tiempo y vencidas

## Fase 1 — Etiquetas (backend)

- [x] **T-3.$1 — Modelos y migración**
  - **Qué hacer:** Modelos `Tag`, `task_tags`, `TimeEntry` y columna `Task.completed_at`;
    migración Alembic (tablas + índice único `lower(name)` de tags + índice único de
    task_tags).
  - **RF:** RF-3.1–3.11 (modelo).
  - **Hecho cuando:** `alembic upgrade head` aplica y `alembic check` sin pendientes.

- [x] **T-3.$1 — Repositorio de etiquetas**
  - **Qué hacer:** `tag_repository.py` (get/list por nombre case-insensitive, create con
    color, delete, vinculación task↔tag sin duplicados).
  - **RF:** RF-3.1–3.5.
  - **Hecho cuando:** tests del repo cubren unicidad, color y desvinculación.

- [x] **T-3.$1 — Servicio y rutas de etiquetas**
  - **Qué hacer:** `tag_service.py` (crear con color autoasignado, eliminar) y rutas
    `/tags` + asignar/quitar en `/tasks/{id}/tags`; `TaskOut` con `tags`.
  - **RF:** RF-3.1–3.6.
  - **Hecho cuando:** tests unitarios y de rutas pasan (409 duplicado, 404).

## Fase 2 — Tiempo y racha (backend)

- [x] **T-3.$1 — completed_at y registro de tiempo**
  - **Qué hacer:** `TaskService.update` setea/limpia `completed_at`; `time_entry_repository`
    y rutas `POST/GET /time-entries`.
  - **RF:** RF-3.8, RF-3.9.
  - **Hecho cuando:** tests cubren el set/limpieza de `completed_at` y el alta de tiempo.

- [x] **T-3.$1 — Estadísticas y racha**
  - **Qué hacer:** `stats_service.py` (racha + agregados por día/etiqueta/proyecto) y
    `GET /stats`.
  - **RF:** RF-3.10, RF-3.11.
  - **Hecho cuando:** tests de racha (huecos, hoy sin actividad, sin completadas) y de
    agregados pasan.

## Fase 3 — Frontend

- [x] **T-3.$1 — Etiquetas en la UI**
  - **Qué hacer:** Gestor de etiquetas (crear/listar/eliminar), chips en la tarjeta y en el
    formulario de tarea, y filtro por etiqueta en el tablero.
  - **RF:** RF-3.1–3.6.
  - **Hecho cuando:** se crean, asignan y filtran etiquetas; `npm test` verde.

- [x] **T-3.$1 — Vencidas y recordatorios**
  - **Qué hacer:** Badge "Vencida"/"Próxima" en tarjeta y contador; lógica sobre
    `due_date`+`completed_at`.
  - **RF:** RF-3.7.
  - **Hecho cuando:** una tarea vencida se muestra en rojo y con el texto correcto.

- [x] **T-3.$1 — Registro de tiempo y panel de estadísticas**
  - **Qué hacer:** Registro rápido de minutos por tarea, y panel con racha, días
    estudiados y minutos por día/etiqueta/proyecto.
  - **RF:** RF-3.8–3.11.
  - **Hecho cuando:** se registra tiempo y el panel muestra racha y agregados reales.

## Fase 4 — Cierre

- [x] **T-3.$1 — Verificación final**
  - **Qué hacer:** `pytest -q`, `ruff`, `npm run build`, `npm test`.
  - **Hecho cuando:** todo verde y flujo completo verificado contra la API.
