# Spec 001 — Gestión de proyectos y tareas

## Contexto y objetivo

TaskFlow es una API para la gestión de proyectos y tareas. Permite a los usuarios
crear y administrar proyectos, crear tareas asociadas, consultarlas con su estado y
prioridad, y controlar su ciclo de vida. El objetivo de esta spec es definir el MVP:
CRUD completo de proyectos y tareas con autenticación de usuarios, listados filtrables
y reglas de negocio que preserven la integridad del trabajo.

## Usuarios

- **Usuario autenticado**: puede registrarse, iniciar sesión y gestionar proyectos y
  tareas. Toda operación de la API requiere sesión válida.

## Historias de usuario

- **US-1**: Como usuario, quiero registrarme e iniciar sesión para acceder a mis datos.
- **US-2**: Como usuario, quiero crear un proyecto para organizar mi trabajo.
- **US-3**: Como usuario, quiero consultar y editar un proyecto para mantener su información al día.
- **US-4**: Como usuario, quiero inactivar un proyecto cuando ya no sea necesario.
- **US-5**: Como usuario, quiero crear tareas dentro de un proyecto para planificar el trabajo.
- **US-6**: Como usuario, quiero actualizar una tarea para registrar su avance.
- **US-7**: Como usuario, quiero consultar mis tareas con filtros, orden y paginación.
- **US-8**: Como usuario, quiero eliminar tareas que ya no necesito.

## Requisitos funcionales

### Autenticación

- **RF-1** — Registro. CUANDO un usuario se registra con credenciales válidas y no
  existentes, ENTONCES el sistema DEBE crear la cuenta. SI el nombre de usuario o correo
  ya existe, ENTONCES el sistema DEBE rechazar el registro e informar en español.
- **RF-2** — Inicio de sesión. CUANDO un usuario inicia sesión con credenciales
  correctas, ENTONCES el sistema DEBE autenticarlo. SI las credenciales son incorrectas,
  ENTONCES el sistema DEBE rechazarlo e informar en español.
- **RF-3** — Acceso protegido. CUANDO una operación de la API se solicita sin una sesión
  válida, ENTONCES el sistema DEBE rechazarla e informar en español.

### Proyectos

- **RF-4** — Crear proyecto. CUANDO el usuario envía un nombre de proyecto válido,
  ENTONCES el sistema DEBE crear el proyecto con estado activo. SI el nombre ya existe,
  ENTONCES el sistema DEBE rechazar la creación e informar en español que el proyecto ya existe.
- **RF-5** — Consultar proyecto. CUANDO el usuario solicita un proyecto existente,
  ENTONCES el sistema DEBE devolver sus datos. SI el proyecto no existe, ENTONCES el
  sistema DEBE informar en español.
- **RF-6** — Editar proyecto. CUANDO el usuario actualiza un proyecto con datos válidos,
  ENTONCES el sistema DEBE guardar los cambios respetando la unicidad del nombre.
- **RF-7** — Inactivar proyecto. CUANDO todas las tareas del proyecto están completadas,
  ENTONCES el sistema DEBE marcar el proyecto como inactivo. SI el proyecto tiene tareas
  sin completar, ENTONCES el sistema DEBE bloquear la inactivación e informar en español
  que todas las tareas deben estar completadas. El proyecto NO se elimina físicamente.

### Tareas

- **RF-8** — Crear tarea. CUANDO el usuario crea una tarea en un proyecto existente,
  ENTONCES el sistema DEBE crearla con estado `TODO` y prioridad `medium` si no se
  especifica otra. SI el proyecto referenciado no existe, ENTONCES el sistema DEBE
  rechazar la creación e informar en español que el proyecto no existe.
- **RF-9** — Consultar tarea. CUANDO el usuario solicita una tarea existente, ENTONCES el
  sistema DEBE devolver sus datos. SI la tarea no existe, ENTONCES el sistema DEBE
  informar en español.
- **RF-10** — Listar tareas. CUANDO el usuario consulta las tareas de un proyecto,
  ENTONCES el sistema DEBE permitir filtrar por estado y prioridad, ordenar por prioridad
  o fecha límite y paginar resultados.
- **RF-11** — Actualizar tarea. CUANDO el usuario actualiza una tarea que no está en
  `DONE`, ENTONCES el sistema DEBE guardar los cambios. SI la tarea está en `DONE`,
  ENTONCES el sistema DEBE bloquear la actualización e informar en español.
- **RF-12** — Transición de estado. CUANDO el estado de una tarea cambia, ENTONCES el
  sistema DEBE permitir únicamente avances progresivos `TODO` → `IN_PROGRESS` → `DONE`.
  SI se intenta una transición hacia atrás, ENTONCES el sistema DEBE rechazarla e
  informar en español.
- **RF-13** — Eliminar tarea. CUANDO el usuario elimina una tarea, ENTONCES el sistema
  DEBE eliminarla junto con su información.

## Requisitos no funcionales

- **RNF-1** — Los mensajes de error funcionales y de usuario están en español; el código
  y los identificadores, en inglés.
- **RNF-2** — Los datos persistidos no se pierden ante reinicios del sistema.
- **RNF-3** — Las credenciales de los usuarios nunca se almacenan en claro.
- **RNF-4** — La API responde de forma consistente y con tiempos razonables para volúmenes
  típicos del MVP.
- **RNF-5** — Toda funcionalidad se entrega con tests automatizados.

## Casos límite

- Crear una tarea referenciando un proyecto inexistente.
- Crear un proyecto con nombre duplicado (ver duda abierta sobre sensibilidad a mayúsculas).
- Inactivar un proyecto con tareas sin completar.
- Actualizar o transicionar una tarea que ya está en `DONE`.
- Transición de estado hacia atrás (`DONE` → `IN_PROGRESS`).
- Credenciales de registro o inicio de sesión inválidas.
- Operación sin sesión válida.
- Página de resultados fuera de rango o sin resultados para los filtros aplicados.
- Campos obligatorios vacíos o fecha límite inválida.

## Fuera de alcance

- Roles y permisos avanzados (existe un único tipo de usuario).
- El modal de auto-creación de proyecto (experiencia de frontend; la API solo debe
  comunicar claramente que el proyecto no existe).
- Notificaciones, comentarios, subtareas y dependencias entre tareas.
- Adjuntos y archivos.
- Búsqueda por texto libre.
- Recuperación o restablecimiento de contraseña.
- Internacionalización (el idioma de la API es solo español).

## Criterios de finalización

- Todos los RF-1 a RF-13 están implementados y cumplen sus criterios de aceptación.
- `pytest -q` pasa sin errores.
- Las reglas de negocio (duplicados, bloqueos, transiciones, inactivación) están cubiertas por tests.
- No existe funcionalidad fuera de lo contemplado en esta spec.
- Documentación y mensajes en español; código en inglés.

## Dudas abiertas [NECESITA ACLARACIÓN]

- ¿Cada usuario gestiona solo sus propios proyectos y tareas, o son compartidos entre todos los usuarios?
- ¿Eliminar una tarea es borrado físico o también se inactiva como los proyectos?
- ¿El campo "usuario asignado" es obligatorio y a qué usuarios puede asignarse?
- ¿La unicidad del nombre de proyecto distingue mayúsculas/minúsculas o es insensible?
- El mecanismo concreto de autenticación (p. ej. token) y la expiración de sesión se decidirán en el plan.
