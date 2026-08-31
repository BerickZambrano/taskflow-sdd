# Tareas — Gestión de proyectos y tareas

Lista de implementación derivada de `spec.md` y `plan.md`. Cada tarea dura ~20-30 min.
No introducen funcionalidad fuera de la spec. Ordenadas por dependencias.

## Fase 1 — Infraestructura base

- [x] **T-1 — Estructura del proyecto**
  - **Qué hacer:** Crear `pyproject.toml` (Python 3.12, deps del plan §5), `Dockerfile`,
    `docker-compose.yml` (servicio PostgreSQL con volumen), `.env.example` y `.gitignore`.
    Añadir `ruff` como herramienta de lint/formato.
  - **RF:** base para todos (principios 1 y 5).
  - **Hecho cuando:** `ruff check .` y `ruff format --check .` pasan sobre un
    `app/main.py` mínimo con la app FastAPI y `GET /health` que responde `200`.

- [x] **T-2 — Configuración del entorno**
  - **Qué hacer:** Implementar `app/core/config.py` con `pydantic-settings` leyendo
    variables de entorno (BD, secreto JWT, expiración de token) y validar su carga.
  - **RF:** base (RNF-2/RNF-3).
  - **Hecho cuando:** la app se inicializa con valores de entorno y falla de forma
    clara si falta una variable obligatoria.

- [x] **T-3 — Modelos de datos y migración inicial**
  - **Qué hacer:** Crear modelos SQLAlchemy `User`, `Project` y `Task` (plan §2),
    enums (`TaskStatus`, `Priority`, `ProjectStatus`) y la migración Alembic inicial que
    crea las tres tablas con sus FKs, unicidades e índices.
  - **RF:** RF-1 a RF-13 (modelo de datos).
  - **Hecho cuando:** `alembic upgrade head` crea el esquema en PostgreSQL y
    `alembic check` indica que no hay cambios pendientes.

## Fase 2 — Núcleo compartido

- [x] **T-4 — Excepciones de dominio y manejadores HTTP**
  - **Qué hacer:** Implementar `app/core/exceptions.py` con excepciones de dominio
    (p. ej. `NotFoundError`, `ConflictError`, `UnauthorizedError`) y manejadores globales
    que devuelvan `{"detail": "<mensaje en español>"}` con los códigos del contrato (§4).
  - **RF:** RF-3 (respuestas de error) y todos los RF (formato de errores).
  - **Hecho cuando:** lanzar cada excepción desde una ruta de prueba devuelve el código
    y mensaje en español esperados.

- [x] **T-5 — Seguridad: hash de contraseñas y JWT**
  - **Qué hacer:** Implementar `app/core/security.py` con hash bcrypt (pwdlib) y
    creación/validación de tokens JWT (PyJWT) con expiración configurable.
  - **RF:** RF-1, RF-2, RF-3 (RNF-3).
  - **Hecho cuando:** un hash se verifica correctamente y difiere del texto claro; un
    token firmado se valida y un token vencido o inválido se rechaza.

## Fase 3 — Autenticación

- [x] **T-6 — Repositorio de usuarios**
  - **Qué hacer:** Implementar `app/repositories/user_repository.py` con operaciones de
    creación y búsqueda por `username`, `email` e `id`.
  - **RF:** RF-1, RF-2.
  - **Hecho cuando:** las búsquedas devuelven los registros correctos y la creación
    persiste sin duplicar `username`/`email`.

- [x] **T-7 — Servicio de autenticación**
  - **Qué hacer:** Implementar `app/services/auth_service.py`: registro (rechaza
    `username`/`email` duplicados con `409`) y login (valida credenciales, devuelve
    token; credenciales incorrectas → `401`).
  - **RF:** RF-1, RF-2.
  - **Hecho cuando:** los tests unitarios cubren: registro exitoso, duplicados `409`,
    login exitoso, credenciales inválidas `401`, y mensajes en español.

- [x] **T-8 — Rutas de autenticación y dependencia de sesión**
  - **Qué hacer:** Implementar schemas y rutas `POST /auth/register` y
    `POST /auth/login`, y la dependencia `get_current_user` que exige token `Bearer`
    válido (si no → `401`) para el resto de rutas.
  - **RF:** RF-1, RF-2, RF-3.
  - **Hecho cuando:** registrarse devuelve `201`, el login devuelve
    `{access_token, token_type:"bearer"}`, y las rutas protegidas devuelven `401` sin
    token válido.

## Fase 4 — Proyectos

- [x] **T-9 — Repositorio de proyectos**
  - **Qué hacer:** Implementar `app/repositories/project_repository.py`: CRUD básico y
    búsqueda por nombre (insensible a mayúsculas) por propietario.
  - **RF:** RF-4 a RF-7.
  - **Hecho cuando:** las operaciones persisten correctamente y la búsqueda por nombre
    distingue correctamente duplicados del mismo propietario.

- [x] **T-10 — Servicio de proyectos**
  - **Qué hacer:** Implementar `app/services/project_service.py` con las reglas: crear
    (nombre duplicado → `409`), consultar/listar, editar (respeta unicidad), e inactivar
    (solo si todas las tareas están `done`; si no → `409`; no borra físicamente).
  - **RF:** RF-4, RF-5, RF-6, RF-7.
  - **Hecho cuando:** tests unitarios cubren crear, listar, consultar, editar, duplicado
    `409`, e inactivación bloqueada con tareas pendientes y permitida con todas `done`.

- [x] **T-11 — Rutas de proyectos**
  - **Qué hacer:** Implementar schemas y rutas `GET/POST /projects`,
    `GET/PATCH/DELETE /projects/{id}` con alcance por propietario (`404` si no existe o
    no es del usuario) y códigos del contrato (§4).
  - **RF:** RF-4 a RF-7.
  - **Hecho cuando:** cada endpoint responde el código y mensaje esperado en los casos
    de éxito y error del contrato.

## Fase 5 — Tareas

- [x] **T-12 — Repositorio de tareas**
  - **Qué hacer:** Implementar `app/repositories/task_repository.py`: CRUD básico y
    consulta filtrable (estado, prioridad), ordenable (prioridad, fecha límite) y
    paginable, por proyecto.
  - **RF:** RF-8 a RF-13.
  - **Hecho cuando:** la consulta aplica filtros, orden y paginación devolviendo
    `{items, total, page, page_size}` correctos.

- [x] **T-13 — Servicio de tareas**
  - **Qué hacer:** Implementar `app/services/task_service.py` con las reglas: crear con
    default `todo`/`medium` y `404` si el proyecto no existe; actualizar bloqueada si la
    tarea está `done` (`409`); transiciones solo un paso hacia adelante (`409` si se
    retrocede); eliminar con borrado físico.
  - **RF:** RF-8, RF-9, RF-11, RF-12, RF-13.
  - **Hecho cuando:** tests unitarios cubren defaults, `404` de proyecto, bloqueo de
    tarea `done`, transiciones válidas/inválidas y borrado.

- [x] **T-14 — Rutas de tareas**
  - **Qué hacer:** Implementar schemas y rutas `POST /projects/{project_id}/tasks`,
    `GET /projects/{project_id}/tasks`, `GET/PATCH/DELETE /tasks/{id}` con alcance por
    propietario y códigos del contrato (§4).
  - **RF:** RF-8 a RF-13.
  - **Hecho cuando:** cada endpoint responde el código y mensaje esperado en los casos
    de éxito y error del contrato (incluye filtros, orden y paginación).

## Fase 6 — Tests de integración

- [x] **T-15 — Fixtures y tests de autenticación**
  - **Qué hacer:** Crear `tests/conftest.py` (cliente autenticado, BD PostgreSQL de
    test con migraciones Alembic, fábricas) y `tests/test_auth.py` para RF-1, RF-2, RF-3.
  - **RF:** RF-1, RF-2, RF-3.
  - **Hecho cuando:** los tests de registro, login y acceso protegido pasan y verifican
    códigos HTTP y mensajes en español.

- [x] **T-16 — Tests de integración de proyectos**
  - **Qué hacer:** Escribir `tests/test_projects.py` cubriendo cada criterio de
    aceptación de RF-4 a RF-7 a través de la API (incluye `404` de recursos ajenos).
  - **RF:** RF-4 a RF-7.
  - **Hecho cuando:** todos los casos de éxito y error de los RF-4..RF-7 pasan.

- [x] **T-17 — Tests de integración de tareas**
  - **Qué hacer:** Escribir `tests/test_tasks.py` cubriendo RF-8 a RF-13 a través de la
    API (defaults, filtros/orden/paginación, bloqueo `done`, transiciones, borrado).
  - **RF:** RF-8 a RF-13.
  - **Hecho cuando:** todos los casos de éxito y error de los RF-8..RF-13 pasan.

## Fase 7 — Cierre

- [x] **T-18 — Verificación final**
  - **Qué hacer:** Ejecutar la suite completa y la verificación manual de los endpoints
    afectados según el plan §7.
  - **RF:** RNF-5, principio 4.
  - **Hecho cuando:** `pytest -q`, `ruff check .` y `ruff format --check .` pasan sin
    errores y no hay secretos ni archivos fuera del alcance en el repo.
