# Tareas — Interfaz web (frontend)

Lista de implementación derivada de `spec.md` y `plan.md` (spec 002). ~30-45 min/tarea.
No introducen funcionalidad fuera de la spec. Ordenadas por dependencias.

## Fase 1 — Base

- [x] **F-1 — Scaffold del proyecto**
  - **Qué hacer:** Crear el proyecto Vite (React + TS) en `frontend/`, con `package.json`,
    `vite.config.ts` (proxy a la API), `tsconfig`, `index.html` y tipografías.
  - **RF:** base (todas).
  - **Hecho cuando:** `npm run dev` levanta la app y `npm run build` compila sin errores.

- [x] **F-2 — Sistema de diseño**
  - **Qué hacer:** Crear `tokens.css` (variables claro/oscuro), `base.css` y `components.css`
    con botones, inputs, badges, modal, barra de progreso y toggle de tema.
  - **RF:** RNF-3, RF-10 (tema).
  - **Hecho cuando:** el tema claro/oscuro se aplica vía una clase en `<html>` y los
    componentes base se ven correctamente.

## Fase 2 — Datos y autenticación

- [x] **F-3 — Cliente API y tipos**
  - **Qué hacer:** Crear `api/types.ts` y `api/client.ts` (fetch con token, traducción de
    errores `401/404/409/422` a español, expulsión en `401`).
  - **RF:** RF-2, RNF-1, casos límite de errores.
  - **Hecho cuando:** los tests del cliente cubren éxito, errores traducidos y `401`.

- [x] **F-4 — Login y registro**
  - **Qué hacer:** Crear `AuthPage.tsx` con login/registro, validación y mensajes de la
    API; guardar el token en `localStorage`.
  - **RF:** RF-1, RF-2.
  - **Hecho cuando:** iniciar sesión lleva a la app, registrar crea cuenta, y los errores
    se muestran en español.

## Fase 3 — Shell y proyectos

- [x] **F-5 — Shell, sidebar y proyectos**
  - **Qué hacer:** Crear `AppShell`/`Sidebar` (lista de proyectos, selección, crear
    proyecto con `ProjectForm`, progreso por proyecto, cerrar sesión, toggle de tema).
  - **RF:** RF-3, RF-10 (progreso/tema).
  - **Hecho cuando:** se listan, seleccionan y crean proyectos; el progreso y el tema se
    actualizan correctamente.

## Fase 4 — Tareas

- [x] **F-6 — Vista de tareas**
  - **Qué hacer:** Crear `ProjectView` (cabecera con meta y acciones), filtros por
    estado/prioridad, orden y paginación, y `TaskCard` (estado, prioridad, fecha límite).
  - **RF:** RF-4, RF-10 (vacíos/carga).
  - **Hecho cuando:** las tareas se filtran, ordenan y paganinan contra la API.

- [x] **F-7 — Crear, editar y transiciones**
  - **Qué hacer:** Crear `TaskForm` (crear/editar), acciones de avance de estado paso a
    paso, bloqueo de edición de tareas `done` y avisos en español.
  - **RF:** RF-5, RF-6, RF-7.
  - **Hecho cuando:** se crean y editan tareas, las transiciones son progresivas y una
    tarea `done` no se puede editar.

- [x] **F-8 — Modal de proyecto inexistente e inactivar**
  - **Qué hacer:** Crear `ProjectMissingModal` (crea el proyecto y continúa la tarea
    pendiente) y la acción de inactivar proyecto con confirmación y aviso si quedan
    tareas pendientes.
  - **RF:** RF-8, RF-9.
  - **Hecho cuando:** el flujo del modal y la inactivación funcionan contra la API.

## Fase 5 — Cierre

- [x] **F-9 — Verificación final**
  - **Qué hacer:** Tests de componentes (Vitest), revisión responsive, estados de
    carga/vacío/error y build de producción.
  - **RF:** RNF-5, criterios de finalización.
  - **Hecho cuando:** `npm test` y `npm run build` pasan sin errores y el flujo completo
    funciona contra la API en ejecución.
