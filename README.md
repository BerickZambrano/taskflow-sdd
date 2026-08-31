# TaskFlow

TaskFlow es una herramienta personal para organizar **proyectos y estudios**: proyectos,
tareas en un tablero Kanban, etiquetas por materia, registro de tiempo y estadísticas de
constancia (racha). La interfaz está en español; el código y los identificadores, en inglés.

## Stack

**Backend**
- Python 3.12+, FastAPI
- PostgreSQL (fuente de verdad) + SQLAlchemy 2.0 + Alembic (migraciones)
- Autenticación con JWT (Bearer) y contraseñas con hash bcrypt
- Docker para el entorno de ejecución

**Frontend**
- React 19 + Vite + TypeScript
- CSS propio con tema claro/oscuro (sin librería de componentes)
- Vitest + React Testing Library

## Funcionalidades

- Registro e inicio de sesión con sesión persistente.
- Proyectos: crear, editar, inactivar (solo si todas las tareas están completadas) y
  reactivar.
- Tareas: CRUD completo con listado filtrable (estado, prioridad, etiqueta), orden y
  tablero Kanban con columnas por estado.
- Transiciones de estado **progresivas** (`todo → in_progress → done`); no se permite
  retroceder ni saltar pasos.
- Etiquetas/áreas con color autoasignado para agrupar tareas entre proyectos.
- Detección de tareas **vencidas** y **próximas** a vencer.
- Registro de tiempo por tarea y estadísticas: racha de días con tareas completadas,
  días estudiados, minutos totales y por día/etiqueta/proyecto.
- Tema claro/oscuro, responsive y mensajes de error en español.

## Desarrollo dirigido por especificaciones (SDD)

El proyecto se construyó con **Spec Driven Development** usando el modelo **DeepSeek V4**
como asistente de desarrollo. El flujo seguido en cada funcionalidad fue:

1. **Constitución** (`docs/constitution.md`): 6 principios innegociables del proyecto.
2. **Spec** (`specs/<id>/spec.md`): el QUÉ y el POR QUÉ, con requisitos funcionales en
   notación EARS y criterios de aceptación.
3. **Plan** (`specs/<id>/plan.md`): el CÓMO, con arquitectura, contrato, decisiones
   técnicas y la alternativa descartada.
4. **Tasks** (`specs/<id>/tasks.md`): tareas pequeñas, ordenadas y verificables.
5. **Código + tests**: implementación que cumple los criterios de aceptación y
   `pytest -q`/`npm test` en verde.

> ¿Por qué SDD? Garantiza que no se implementa nada fuera de lo especificado, que cada
> cambio queda documentado y que la funcionalidad es verificable de forma objetiva.
> Con un modelo como DeepSeek V4, el SDD ayuda a mantener coherencia y trazabilidad
> en cada iteración.

La funcionalidad se organiza en estas especificaciones:

| Spec | Alcance |
|---|---|
| `001-task-management` | API: autenticación, proyectos y tareas (CRUD, reglas de negocio). |
| `002-web-frontend` | Interfaz web: login, sidebar, tablero, modales, tema. |
| `003-tags-stats` | Etiquetas, tareas vencidas, tiempo y estadísticas/racha. |

## Requisitos para desarrollo

- Python 3.12+
- PostgreSQL 16+ (crear el rol y las bases `taskflow` y `taskflow_test`)
- Node.js 20+ y npm
- (Opcional) Docker

## Puesta en marcha

### 1. Base de datos

Crea el rol y las bases (una vez):

```sql
CREATE ROLE taskflow LOGIN PASSWORD 'taskflow';
CREATE DATABASE taskflow OWNER taskflow;
CREATE DATABASE taskflow_test OWNER taskflow;
```

Configura la conexión en `.env` (copia de `.env.example`):

```
DATABASE_URL=postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow
SECRET_KEY=tu-secreto-largo
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 2. Backend

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
alembic upgrade head            # migraciones
uvicorn app.main:app --reload   # http://localhost:8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

El dev server de Vite hace proxy de `/auth`, `/projects`, `/tasks`, `/tags`,
`/time-entries` y `/stats` hacia el backend en `http://localhost:8000`.

## Comandos de calidad

| Qué | Backend | Frontend |
|---|---|---|
| Tests | `pytest -q` | `npm test` |
| Lint | `ruff check .` | `npm run lint` |
| Formato | `ruff format --check .` | — |
| Build | — | `npm run build` |
| Ejecutar | `uvicorn app.main:app --reload` | `npm run dev` |

## Arquitectura

Separación estricta de capas (constitución, principio 3):

```
Cliente → API (rutas + schemas) → Servicios (reglas de negocio) → Repositorios (SQL) → PostgreSQL
```

- `app/api/` — rutas HTTP y schemas Pydantic (validación).
- `app/services/` — lógica de negocio (reglas: unicidad, transiciones, inactivación, racha).
- `app/repositories/` — acceso a datos (SQLAlchemy), sin reglas de negocio.
- `app/models/` — modelos ORM; `alembic/` — migraciones.
- `frontend/` — SPA React (Vite) con cliente API en `src/api/`.

## Documentación

- Constitución: `docs/constitution.md`
- Especificaciones: `specs/`
- Guía para agentes/asistentes: `AGENTS.md`
