import type { ProjectOut } from '../api/types'
import { ProgressBar } from './ui'
import { LogoutIcon, MoonIcon, PlusIcon, SunIcon } from './icons'

// Tipo con conteos para el progreso (rellenado en AppShell)
export type ProjectWithStats = ProjectOut & { done: number; total: number }

interface SidebarProps {
  projects: ProjectWithStats[]
  selectedId: string | null
  username: string
  theme: 'light' | 'dark'
  onSelect: (id: string) => void
  onCreateNew: () => void
  onToggleTheme: () => void
  onLogout: () => void
}

export function Sidebar({
  projects,
  selectedId,
  username,
  theme,
  onSelect,
  onCreateNew,
  onToggleTheme,
  onLogout,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-head">
        <span className="sidebar-wordmark">TaskFlow</span>
        <button
          className="icon-btn"
          onClick={onToggleTheme}
          title={theme === 'light' ? 'Cambiar a modo oscuro' : 'Cambiar a modo claro'}
          aria-label="Cambiar tema"
        >
          {theme === 'light' ? <MoonIcon /> : <SunIcon />}
        </button>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-label">Proyectos</div>
        <ul className="project-list">
          {projects.map((project) => {
            const active = project.id === selectedId
            return (
              <li key={project.id}>
                <button
                  className={`project-item ${active ? 'active' : ''}`}
                  onClick={() => onSelect(project.id)}
                  title={project.name}
                >
                  <span className="project-name">{project.name}</span>
                  {project.status === 'inactive' && (
                    <span className="project-inactive">archivado</span>
                  )}
                  <span className="project-progress">
                    <ProgressBar
                      value={project.done}
                      total={project.total}
                    />
                  </span>
                </button>
              </li>
            )
          })}
        </ul>
      </div>

      <button className="btn btn-ghost new-project" onClick={onCreateNew}>
        <PlusIcon />
        Nuevo proyecto
      </button>

      <div className="sidebar-foot">
        <span className="sidebar-user">{username}</span>
        <button className="icon-btn" onClick={onLogout} title="Cerrar sesión" aria-label="Cerrar sesión">
          <LogoutIcon />
        </button>
      </div>
    </aside>
  )
}
