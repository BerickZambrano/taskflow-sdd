# AGENTS.md — taskflow-sdd 

## Proyecto

API REST para la gestión de proyectos y tareas. Permite a los usuarios crear proyectos, administrar tareas y consultar su estado y progreso.

Backend desarrollado con Python y FastAPI, con PostgreSQL como base de datos y Docker para el entorno de ejecución.

## Comandos

* Ejecutar: `uvicorn app.main:app --reload`
* Tests: `pytest -q`
* Lint: `ruff check .`
* Formato: `ruff format .`

## Estilo

* Python 3.12+.
* Type hints en todas las funciones públicas.
* Seguir PEP 8 y las convenciones de Python.
* Identificadores, nombres de archivos, endpoints y código en inglés.
* Documentación y mensajes de usuario en español.
* Clases en `PascalCase`.
* Funciones, variables y módulos en `snake_case`.
* Constantes en `UPPER_SNAKE_CASE`.
* Commits siguiendo Conventional Commits.

## Reglas

* Lee `docs/constitution.md` y la spec activa en `specs/` antes de tocar código.
* No implementes funcionalidades que no estén contempladas en la spec activa.
* No añadas dependencias sin actualizar previamente la documentación correspondiente.
* No cambies la arquitectura o estructura de datos sin actualizar antes la spec.
* No almacenes secretos, API keys o credenciales en el código.
* Utiliza variables de entorno para configuraciones sensibles.
* Mantén separadas las responsabilidades de API, lógica de negocio y acceso a datos.
* No modifiques archivos dentro de `specs/` salvo que la tarea lo solicite explícitamente.
* Los cambios que afecten al comportamiento de la API deben incluir o actualizar sus tests.

## Al terminar cualquier tarea

* Ejecuta `pytest -q` y confirma en tu respuesta que todos los tests pasan.
* Ejecuta `ruff check .`.
* Ejecuta `ruff format --check .`.
* Verifica manualmente los endpoints afectados cuando corresponda.
* Confirma que no se hayan introducido secretos ni cambios fuera del alcance de la tarea.
