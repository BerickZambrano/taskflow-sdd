# Plan 002 — Interfaz web (frontend)

Define CÓMO se implementa la spec 002 contra la API de la spec 001. Mensajes en español,
código en inglés. Tema claro/oscuro, sidebar + área principal.

## 1. Stack y estructura

Stack: **Vite + React 18 + TypeScript**, CSS propio (sin librería UI), `fetch` nativo,
**Vitest + React Testing Library** para tests. Proxy de Vite a la API en dev.

```
frontend/
  index.html
  package.json
  vite.config.ts        # proxy /auth, /projects, /tasks -> http://localhost:8000
  src/
    main.tsx
    App.tsx             # máquina de estados: auth, proyecto seleccionado, tema
    api/
      client.ts         # fetch con token, manejo de 401/409/404/422
      types.ts          # tipos alineados con la API (spec 001)
    components/
      AuthPage.tsx      # login/registro (RF-1)
      AppShell.tsx      # sidebar + área principal (RF-3)
      Sidebar.tsx       # lista de proyectos + progreso + crear (RF-3, RF-10)
      ProjectView.tsx   # cabecera + filtros + lista de tareas (RF-4)
      TaskCard.tsx      # tarea con acciones de estado/edición (RF-6, RF-7)
      TaskForm.tsx      # crear/editar tarea (RF-5, RF-7)
      ProjectForm.tsx   # crear proyecto (RF-3, RF-9)
      ProjectMissingModal.tsx  # flujo RF-9
      Modal.tsx         # diálogo reutilizable
      icons.tsx         # iconos SVG propios
      ui.tsx            # botones, inputs, badge, toggle de tema (RF-10)
    styles/
      tokens.css        # variables de tema claro/oscuro
      base.css
      components.css
    test/               # tests Vitest (RF-5, RF-9, client)
```

## 2. Decisiones técnicas justificadas (y alternativa descartada)

| Decisión | Justificación | Alternativa descartada |
|---|---|---|
| React + Vite + TS | Elegido por el producto; ecosistema maduro, tipado | Vue/Svelte — no elegidos |
| CSS propio con variables | Estilo diferenciado (no genérico), control total, sin dep | Tailwind/Chakra — dep extra y estética genérica |
| `fetch` nativo | Sin dependencias para HTTP | axios — innecesario |
| Estado por vista (sin router) | SPA pequeña: sidebar decide la vista | react-router — complejidad innecesaria |
| Token en `localStorage` | Sesión persistente (RF-2) | cookies con backend — requiere cambios en la API |
| Vitest + Testing Library | Tests rápidos en Node (RNF-5) | Cypress E2E — pesado para el MVP |

## 3. Sistema de diseño

- **Tipografía**: serif (Fraunces) para marca/títulos y sans (Inter) para UI/lectura.
- **Paleta claro**: papel `#F6F3EC`, superficie `#FFFFFF`, tinta `#211C15`, acento
  terracota `#C4553A`, success `#47734F`, warning `#C08A2D`.
- **Paleta oscuro**: fondo `#191613`, superficie `#241F19`, tinta `#EFE9DF`,
  acento `#E07A5F`.
- **Detalles**: radios 12px, bordes 1px cálidos, sombras suaves, estados hover/focus,
  chips de estado con punto de color, prioridad como barras (L/M/H), barra de progreso
  del proyecto.

## 4. Contrato con la API

Reutiliza los endpoints de la spec 001/plan 001 (register, login, projects CRUD,
tasks CRUD + listado con `status`, `priority`, `sort_by`, `order`, `page`, `page_size`).
El cliente traduce errores `401/404/409/422` a mensajes en español.

## 5. Estrategia de tests

- Unitarios del cliente API (errores → mensajes en español, 401 cierra sesión).
- Componentes: formularios de tarea/proyecto y modal RF-9 (render, envío, flujo).
- `npm test` (Vitest) y `npm run build` en el cierre.
