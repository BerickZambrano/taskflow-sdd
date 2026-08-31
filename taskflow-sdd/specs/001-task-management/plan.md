# Plan 001 — Gestión de proyectos y tareas

Este documento define CÓMO se implementa lo definido en `spec.md`. No añade ni modifica
requisitos. Las dudas abiertas de la spec se resuelven con una decisión explícita,
marcada como **[DECISIÓN]**; las que requieren confirmación del producto se señalan como
**[PENDIENTE CONFIRMACIÓN]**. Mensajes de error al usuario: en español. Código e
identificadores: en inglés.

## 1. Estructura de módulos  → cubre RF-1 a RF-13 (principio 3 de la constitución)

Separación estricta de capas: API → lógica de negocio → persistencia.

```
app/
  main.py              # Fábrica de la app, registro de routers y manejadores de errores
  core/
    config.py          # Configuración desde variables de entorno (pydantic-settings)
    enums.py           # TaskStatus, Priority, ProjectStatus
    security.py        # Hash de contraseñas y emisión/validación de tokens
    exceptions.py      # Excepciones de dominio y su mapeo a HTTP
  api/
    deps.py            # Dependencias compartidas (sesión BD, usuario autenticado)
    routes/
      auth.py          # /auth/register, /auth/login            -> RF-1, RF-2
      projects.py      # CRUD de proyectos                       -> RF-4..RF-7
      tasks.py         # CRUD de tareas + listado filtrable     -> RF-8..RF-13
    schemas/           # Pydantic: auth.py, project.py, task.py
  services/            # Lógica de negocio (reglas RF)
    auth_service.py    # Registro/login                         -> RF-1, RF-2
    project_service.py # Duplicados, inactivación               -> RF-4..RF-7
    task_service.py    # Transiciones, bloqueos, filtros        -> RF-8..RF-13
  repositories/        # Acceso a datos (SQLAlchemy)
    user_repository.py
    project_repository.py
    task_repository.py
alembic/               # Migraciones (fuente de verdad del esquema)
  env.py
  versions/
tests/                 # Estrategia en §7
docker-compose.yml     # Servicio PostgreSQL
Dockerfile
pyproject.toml
.env.example
```

**Capa API** (`routes/`): valida la petición con schemas Pydantic y delega en servicios.
**Capa de negocio** (`services/`): aplica las reglas de la spec y lanza excepciones de
dominio. **Capa de persistencia** (`repositories/`): solo SQL; sin reglas de negocio.

## 2. Modelo de datos → cubre RF-1 a RF-13 (principio 5)

Entidades (nombres en inglés, tabla en inglés):

- **User**: `id` (UUID PK), `username` (único), `email` (único), `password_hash`,
  `created_at`, `updated_at`.
- **Project**: `id` (UUID PK), `name`, `description` (nullable), `status`
  (`active|inactive`), `owner_id` (FK User), `created_at`, `updated_at`.
  Unicidad: nombre único **insensible a mayúsculas** por propietario **[DECISIÓN]**.
- **Task**: `id` (UUID PK), `title`, `description` (nullable), `priority`
  (`low|medium|high`, default `medium`), `status` (`todo|in_progress|done`, default
  `todo`), `due_date` (nullable), `assignee_id` (FK User, nullable) **[DECISIÓN: campo
  opcional, asignable a cualquier usuario registrado]** **[PENDIENTE CONFIRMACIÓN]**,
  `project_id` (FK Project), `created_at`, `updated_at`.

Ejemplo JSON:

```json
{
  "id": "8f14e45f-9b2c-4f1e-8a3d-5c6b7a8d9e0f",
  "name": "Lanzamiento web",
  "description": "Proyecto del sitio público",
  "status": "active",
  "owner_id": "aa0f1b2c-3d4e-5f60-7a8b-9c0d1e2f3a4b",
  "created_at": "2026-08-31T10:00:00Z",
  "updated_at": "2026-08-31T10:00:00Z",
  "tasks": [
    {
      "id": "b2c1d3e4-5f60-7a8b-9c0d-1e2f3a4b5c6d",
      "title": "Diseñar landing",
      "description": "Diseño en Figma",
      "priority": "high",
      "status": "in_progress",
      "due_date": "2026-09-15",
      "assignee_id": null
    },
    {
      "id": "c3d2e4f5-6a7b-8c9d-0e1f-2a3b4c5d6e7f",
      "title": "Publicar en producción",
      "priority": "medium",
      "status": "todo",
      "due_date": "2026-09-30"
    }
  ]
}
```

## 3. Diseño de la API REST → cubre RF-1 a RF-13

- Todos los recursos se identifican por UUID.
- Autenticación por token `Bearer` (JWT) en todas las rutas salvo `register`/`login`.
- **Alcance por propietario [DECISIÓN]**: cada usuario accede solo a sus proyectos y
  tareas; los recursos de otro usuario o inexistentes devuelven `404` (sin revelar
  existencia). **[PENDIENTE CONFIRMACIÓN]**
- Errores en formato `{"detail": "<mensaje en español>"}`.
- **Eliminación de tarea: borrado físico [DECISIÓN]** (RF-13). **Proyecto: no se
  elimina; se inactiva [DECISIÓN]** (RF-7).

Flujo de comunicación entre capas (aplica a toda operación):

```
Cliente → [API: schema Pydantic + auth] → [Service: reglas RF] → [Repository: SQL]
                                              ↑        ↓ error de dominio
                                            HTTP (español) ← ExceptionHandler
```

## 4. Contrato de la API → mapea cada RF

### Autenticación

| Método y ruta | Auth | Cuerpo de petición | Respuesta éxito | Errores | RF |
|---|---|---|---|---|---|
| POST `/auth/register` | No | `{username, email, password}` | `201` + usuario | `409` ya existe (username/email); `422` validación | RF-1 |
| POST `/auth/login` | No | `{identifier, password}` | `200` + `{access_token, token_type:"bearer"}` | `401` credenciales incorrectas; `422` | RF-2 |
| Cualquier otra ruta | Bearer | — | — | `401` sin token o inválido | RF-3 |

### Proyectos (requieren Bearer)

| Método y ruta | Cuerpo | Éxito | Errores | RF |
|---|---|---|---|---|
| GET `/projects` | — | `200` lista | — | RF-5 |
| POST `/projects` | `{name, description?}` | `201` | `409` nombre duplicado; `422` | RF-4 |
| GET `/projects/{id}` | — | `200` | `404` no existe | RF-5 |
| PATCH `/projects/{id}` | `{name?, description?, status?}` | `200` | `404`; `409` nombre duplicado; `409` inactivación con tareas pendientes; `422` | RF-6, RF-7b |
| DELETE `/projects/{id}` | — | `204` (inactivado) | `409` tareas sin completar; `404` | RF-7 |

### Tareas (requieren Bearer)

| Método y ruta | Params/cuerpo | Éxito | Errores | RF |
|---|---|---|---|---|
| POST `/projects/{project_id}/tasks` | `{title, description?, priority?, due_date?, assignee_id?}` | `201` (default `todo`/`medium`) | `404` proyecto no existe; `422` | RF-8 |
| GET `/projects/{project_id}/tasks` | `status?`, `priority?`, `sort_by?` (`priority\|due_date`), `order?` (`asc\|desc`), `page?`, `page_size?` | `200` `{items, total, page, page_size}` | `404` proyecto | RF-10 |
| GET `/tasks/{id}` | — | `200` | `404` | RF-9 |
| PATCH `/tasks/{id}` | `{title?, description?, priority?, status?, due_date?, assignee_id?}` | `200` | `409` tarea en `done`; `409` transición inválida; `404`; `422` | RF-11, RF-12 |
| DELETE `/tasks/{id}` | — | `204` | `404` | RF-13 |

### Reglas de negocio implementadas (todas en `services/`)

- **RF-12 — transición de estado**: solo un paso hacia adelante, validado en servicio:

```
ORDEN = {todo: 0, in_progress: 1, done: 2}
SI status no cambia  -> permitido
SI ORDEN[nuevo] == ORDEN[actual] + 1 -> permitido
SI ORDEN[nuevo] <= ORDEN[actual]     -> error 409 "No se puede retroceder el estado de la tarea."
```

- **RF-11**: cualquier actualización de una tarea en `done` → `409` "No se puede
  modificar una tarea completada."
- **RF-7**: inactivar proyecto con tareas no `done` → `409` "Todas las tareas deben
  estar completadas para inactivar el proyecto."
- **RF-7b**: reactivar proyecto (PATCH `status=active`) → `200` con estado `active`.
- **RF-4/RF-6**: duplicado de nombre (insensible a mayúsculas, mismo propietario) → `409`
  "Ya existe un proyecto con ese nombre."
- **RF-8**: proyecto inexistente al crear tarea → `404` "El proyecto no existe."

## 5. Decisiones técnicas justificadas (con alternativa descartada)

| Decisión | Justificación | Alternativa descartada |
|---|---|---|
| SQLAlchemy 2.0 (ORM) + Alembic | Requerido por constitución (migraciones); ORM tipado y mantenible; misma herramienta para migración y acceso | SQL puro con `psycopg` — descartado por migraciones manuales frágiles y acoplamiento de SQL en servicios |
| Stack síncrono (`psycopg` v3) en lugar de asíncrono | Simplicidad (principio 1): menos dependencias y complejidad; FastAPI ejecuta rutas síncronas en threadpool | SQLAlchemy async + `asyncpg` — descartado por añadir complejidad sin necesidad real en el MVP |
| JWT `Bearer` con `PyJWT` | Sesiones sin estado (RF-2/RF-3); simple y escalable; expiración configurable (24 h por defecto) | Sesiones con cookies en servidor — descartado por estado en memoria y complejidad de despliegue |
| Hash de contraseñas con `pwdlib` (bcrypt) | RNF-3: credenciales nunca en claro; librería mantenida y recomendada | `passlib` — descartado (desactualizada); `hashlib` puro — descartado por menor robustez frente a bcrypt |
| UUID como clave primaria | No expone contadores; evita colisiones y facilita agregar réplicas | Auto-incremento entero — descartado por enumerar recursos |
| Pydantic v2 (incluido con FastAPI) para validación | Validación de entrada/salida consistente con `422` en español | Validación manual — descartado por duplicación de esfuerzo y errores |
| Enums de tipo `str` (lowercase) | Valores legibles en JSON (`todo`, `high`, `active`) y validables por Pydantic | Constantes opacas — descartado por menor claridad en el contrato |

**Dependencias** (todas justificadas por la spec): `fastapi`, `uvicorn`, `sqlalchemy`,
`alembic`, `psycopg[binary]`, `pydantic-settings`, `PyJWT`, `pwdlib[bcrypt]`.
Dev: `pytest`, `httpx`, `ruff`. Ninguna sin justificación (principio 1).

## 6. Estrategia de persistencia → cubre RF-1 a RF-13 (principio 5)

- PostgreSQL es la fuente de verdad; todo cambio de esquema vía migración Alembic.
- Acceso exclusivo a través de `repositories/`; transacciones gestionadas por servicio.
- Docker: `docker-compose.yml` con servicio `postgres` (volumen persistente) y app.
- Configuración sensible por variables de entorno (`.env`, no versionado); `.env.example`
  documenta las variables (principio: sin secretos en código).

## 7. Estrategia de tests → cubre todos los RF (RNF-5, principio 4)

- **Unitarios (services/)**: reglas de negocio aisladas de BD con repositorios simulados:
  transiciones RF-12, bloqueo de `done` RF-11, inactivación RF-7, duplicados RF-4/RF-6,
  defaults RF-8.
- **Integración/API (httpx `TestClient`)**: contra una BD PostgreSQL dedicada de test
  (misma tecnología que producción, aplicando migraciones Alembic). Cubren RF-1 a RF-13
  completos, incluyendo códigos HTTP y mensajes en español.
- **Fixtures en `conftest.py`**: cliente autenticado (crea usuario + token) para tests
  protegidos; fábricas de usuario/proyecto/tarea; limpieza de BD por test.
- **Matriz de cobertura**: cada archivo de test mapea a sus RF:
  `test_auth.py` → RF-1, RF-2, RF-3; `test_projects.py` → RF-4 a RF-7;
  `test_tasks.py` → RF-8 a RF-13. Cada criterio de aceptación EARS de la spec tiene al
  menos un test.
- Cierre de tarea: `pytest -q` en verde + `ruff check .` + `ruff format --check .`.

## 8. Dudas abiertas resueltas y pendientes

- **[DECISIÓN]** Tarea eliminada con borrado físico (RF-13); proyecto inactivado (RF-7).
- **[DECISIÓN]** Unicidad de nombre de proyecto insensible a mayúsculas, por propietario.
- **[DECISIÓN]** `assignee_id` opcional, asignable a cualquier usuario registrado.
- **[PENDIENTE CONFIRMACIÓN]** Cada usuario accede solo a sus proyectos/tareas.
- **[PENDIENTE CONFIRMACIÓN]** Expiraciones concretas del token (por defecto 24 h).
