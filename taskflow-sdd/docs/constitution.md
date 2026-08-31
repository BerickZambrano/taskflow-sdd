# Constitución — TaskFlow

Principios innegociables del proyecto. Todo cambio debe cumplirlos.

1. **Simplicidad del stack.** Stack fijo: Python 3.12+, FastAPI, PostgreSQL, Docker. No se añade una dependencia sin justificarla en la spec.
2. **Spec antes que código.** Toda funcionalidad se define en `specs/` con criterios de aceptación antes de implementarse; el código debe cumplirlos.
3. **Separación de capas.** Rutas HTTP, lógica de negocio y acceso a datos viven en módulos separados y no se mezclan.
4. **Tests obligatorios.** Toda funcionalidad nueva incluye o actualiza tests; una tarea solo se cierra si `pytest -q` pasa.
5. **PostgreSQL como fuente de verdad.** Los datos se persisten en PostgreSQL; los cambios de esquema se realizan mediante migraciones y se reflejan en la spec.
6. **Idioma.** Identificadores y código en inglés; documentación, mensajes de usuario y errores funcionales en español.
