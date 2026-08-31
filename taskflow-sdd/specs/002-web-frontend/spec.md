# Spec 002 — Interfaz web (frontend)

## Contexto y objetivo

TaskFlow cuenta con una API REST (spec 001). Esta spec define la interfaz web (SPA en
español) que permite a los usuarios registrarse, iniciar sesión, gestionar proyectos y
tareas consumiendo esa API. El objetivo es ofrecer una experiencia clara y cuidada:
tema claro/oscuro, barra lateral de proyectos y un flujo que anticipe errores (como crear
una tarea en un proyecto inexistente) con diálogos accionables.

## Usuarios

- **Visitante**: puede registrarse o iniciar sesión.
- **Usuario autenticado**: gestiona sus proyectos y tareas.

## Historias de usuario

- **US-1**: Como visitante, quiero registrarme e iniciar sesión para acceder a la app.
- **US-2**: Como usuario, quiero mantener mi sesión abierta entre visitas y poder cerrarla.
- **US-3**: Como usuario, quiero ver y crear proyectos desde la barra lateral.
- **US-4**: Como usuario, quiero ver las tareas de un proyecto con filtros y orden.
- **US-5**: Como usuario, quiero crear tareas con sus campos.
- **US-6**: Como usuario, quiero avanzar el estado de una tarea paso a paso.
- **US-7**: Como usuario, quiero editar una tarea no completada.
- **US-8**: Como usuario, quiero inactivar un proyecto con confirmación.
- **US-9**: Como usuario, quiero recuperar el flujo cuando creo una tarea en un proyecto
  inexistente.
- **US-10**: Como usuario, quiero ver el progreso de cada proyecto y alternar el tema.

## Requisitos funcionales

- **RF-1** — Login y registro. CUANDO el visitante envía credenciales válidas, ENTONCES
  el sistema DEBE autenticarlo; SI son inválidas, ENTONCES el sistema DEBE mostrar un
  error en español. El registro DEBE validar los campos y mostrar los errores de la API.
- **RF-2** — Sesión persistente. CUANDO el usuario inicia sesión, ENTONCES el sistema
  DEBE conservar el token y restaurar la sesión al recargar. CUANDO el usuario cierra
  sesión, ENTONCES el sistema DEBE eliminar el token local.
- **RF-3** — Proyectos en la barra lateral. CUANDO el usuario abre la app, ENTONCES el
  sistema DEBE listar sus proyectos y permitir seleccionar uno y crear otro.
- **RF-4** — Vista de tareas. CUANDO hay un proyecto seleccionado, ENTONCES el sistema
  DEBE mostrar sus tareas con filtros por estado y prioridad, orden por prioridad o fecha
  límite y paginación.
- **RF-5** — Crear tarea. CUANDO el usuario envía una tarea válida, ENTONCES el sistema
  DEBE crearla; SI el proyecto no existe, ENTONCES el sistema DEBE abrir el modal de
  RF-9.
- **RF-6** — Transiciones. CUANDO el usuario avanza una tarea, ENTONCES el sistema DEBE
  permitir solo un paso hacia adelante (`todo` → `in_progress` → `done`). SI la tarea
  está `done`, ENTONCES el sistema DEBE bloquear su edición con un aviso en español.
- **RF-7** — Editar tarea. CUANDO el usuario edita una tarea no completada, ENTONCES el
  sistema DEBE guardar los cambios.
- **RF-8** — Inactivar proyecto. CUANDO el usuario confirma la inactivación, ENTONCES el
  sistema DEBE ejecutarla si todas las tareas están `done`; SI quedan tareas pendientes,
  ENTONCES el sistema DEBE advertirlo sin inactivar.
- **RF-9** — Modal de proyecto inexistente. CUANDO el sistema detecta que el proyecto no
  existe (p. ej. `404`), ENTONCES el sistema DEBE ofrecer crearlo; CUANDO el usuario lo
  confirma, ENTONCES el sistema DEBE crearlo y continuar con la tarea pendiente.
- **RF-10** — Progreso, tema y estados. El sistema DEBE mostrar el porcentaje de tareas
  completadas por proyecto, alternar tema claro/oscuro, y mostrar estados de carga,
  vacíos y errores de forma clara en español.

## Requisitos no funcionales

- **RNF-1** — Mensajes de usuario en español; identificadores y código en inglés.
- **RNF-2** — Accesibilidad básica: foco visible, contraste suficiente, etiquetas en
  formularios.
- **RNF-3** — Diseño responsive y con tema claro/oscuro persistente.
- **RNF-4** — Sin dependencias sin justificar; CSS propio, sin librería de componentes.
- **RNF-5** — Los componentes clave tienen tests automatizados (Vitest).

## Casos límite

- Credenciales incorrectas o campos de registro inválidos.
- Token expirado o inválido (respuesta `401`): cerrar sesión.
- Proyecto sin tareas y proyecto con todas las tareas completadas.
- Crear tarea en un proyecto inexistente.
- Avanzar estado saltando pasos o editar una tarea completada.
- Inactivar un proyecto con tareas pendientes.
- Respuestas de error de la API (`404`, `409`, `422`) mostradas en español.
- Carga inicial sin proyectos.

## Fuera de alcance

- Notificaciones y actualizaciones en tiempo real.
- Gestión de usuarios por un administrador.
- Búsqueda por texto libre.
- PWA / instalación offline.

## Criterios de finalización

- Todos los RF-1 a RF-10 funcionan contra la API real (spec 001).
- `npm run build` compila sin errores y `npm test` pasa.
- Mensajes y textos de la interfaz en español; código en inglés.
- No hay funcionalidad fuera de esta spec.
