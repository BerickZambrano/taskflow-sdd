import { useState } from 'react'

import type { ProjectOut } from '../api/types'
import { Modal } from './Modal'
import { ProjectForm } from './ProjectForm'
import { ProjectView } from './ProjectView'
import { Sidebar, type ProjectWithStats } from './Sidebar'

interface AppShellProps {
  projects: ProjectWithStats[]
  selectedId: string | null
  username: string
  theme: 'light' | 'dark'
  onSelectProject: (id: string) => void
  onProjectCreated: (project: ProjectOut) => void
  onProjectStatusChanged: () => void
  onTaskStatusChanged: (projectId: string) => void
  onToggleTheme: () => void
  onLogout: () => void
}

export function AppShell({
  projects,
  selectedId,
  username,
  theme,
  onSelectProject,
  onProjectCreated,
  onProjectStatusChanged,
  onTaskStatusChanged,
  onToggleTheme,
  onLogout,
}: AppShellProps) {
  const [newProjectOpen, setNewProjectOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const showError = (message: string) => {
    setError(message)
    window.setTimeout(() => setError((current) => (current === message ? null : current)), 4500)
  }

  const selected = projects.find((p) => p.id === selectedId) ?? null

  return (
    <div className="app-shell">
      <Sidebar
        projects={projects}
        selectedId={selectedId}
        username={username}
        theme={theme}
        onSelect={onSelectProject}
        onCreateNew={() => setNewProjectOpen(true)}
        onToggleTheme={onToggleTheme}
        onLogout={onLogout}
      />

      <main className="main-pane">
        {error && (
          <div className="banner" role="alert">
            {error}
            <button className="banner-close" onClick={() => setError(null)} aria-label="Cerrar aviso">
              ×
            </button>
          </div>
        )}

        {selected ? (
          <ProjectView
            key={selected.id}
            project={selected}
            onProjectCreated={onProjectCreated}
            onProjectStatusChanged={onProjectStatusChanged}
            onTaskStatusChanged={onTaskStatusChanged}
            onShowError={showError}
          />
        ) : (
          <div className="empty">
            <div className="empty-title">Elige un proyecto</div>
            <p>Selecciona un proyecto de la lista o crea uno nuevo para empezar.</p>
          </div>
        )}
      </main>

      {newProjectOpen && (
        <Modal title="Nuevo proyecto" onClose={() => setNewProjectOpen(false)}>
          <ProjectForm
            onCreated={(project) => {
              setNewProjectOpen(false)
              onProjectCreated(project)
            }}
            onCancel={() => setNewProjectOpen(false)}
          />
        </Modal>
      )}
    </div>
  )
}
