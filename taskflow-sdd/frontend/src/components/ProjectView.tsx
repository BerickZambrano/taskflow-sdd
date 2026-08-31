import { useCallback, useEffect, useMemo, useState } from 'react'

import { api, ApiError } from '../api/client'
import type { Priority, ProjectOut, TaskDraft, TaskOut, TaskStatus } from '../api/types'
import type { ProjectWithStats } from './Sidebar'
import { Modal } from './Modal'
import { ProjectMissingModal } from './ProjectMissingModal'
import { TaskCard } from './TaskCard'
import { TaskForm } from './TaskForm'
import { Button, EmptyState, ProgressBar, Select, Spinner } from './ui'
import { PlusIcon } from './icons'

interface ProjectViewProps {
  project: ProjectWithStats
  onProjectCreated: (project: ProjectOut) => void
  onProjectStatusChanged: () => void
  onShowError: (message: string) => void
}

const PAGE_SIZE = 20

export function ProjectView({
  project,
  onProjectCreated,
  onProjectStatusChanged,
  onShowError,
}: ProjectViewProps) {
  const [tasks, setTasks] = useState<TaskOut[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)

  const [filterStatus, setFilterStatus] = useState<TaskStatus | ''>('')
  const [filterPriority, setFilterPriority] = useState<Priority | ''>('')
  const [sortBy, setSortBy] = useState<'priority' | 'due_date'>('priority')
  const [order, setOrder] = useState<'asc' | 'desc'>('asc')

  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<TaskOut | null>(null)
  const [missingDraft, setMissingDraft] = useState<TaskDraft | null>(null)
  const [confirmInactive, setConfirmInactive] = useState(false)
  const [advancingId, setAdvancingId] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api.listTasks(project.id, {
        status: filterStatus || undefined,
        priority: filterPriority || undefined,
        sort_by: sortBy,
        order,
        page,
        page_size: PAGE_SIZE,
      })
      setTasks(data.items)
      setTotal(data.total)
    } catch (err) {
      if (err instanceof ApiError) onShowError(err.message)
    } finally {
      setLoading(false)
    }
  }, [project.id, filterStatus, filterPriority, sortBy, order, page, onShowError])

  useEffect(() => {
    setPage(1)
  }, [project.id, filterStatus, filterPriority, sortBy, order])

  useEffect(() => {
    load()
  }, [load])

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / PAGE_SIZE)), [total])

  const closeForm = () => {
    setFormOpen(false)
    setEditing(null)
  }

  const handleSave = async (draft: TaskDraft) => {
    try {
      if (editing) {
        await api.updateTask(editing.id, draft)
      } else {
        await api.createTask(project.id, draft)
      }
      closeForm()
      await load()
    } catch (err) {
      if (err instanceof ApiError && err.status === 404 && !editing) {
        setFormOpen(false)
        setMissingDraft(draft)
        return
      }
      throw err
    }
  }

  const handleMissingProjectCreated = async (created: ProjectOut) => {
    setMissingDraft(null)
    onProjectCreated(created)
    if (missingDraft) {
      try {
        await api.createTask(created.id, missingDraft)
      } catch {
        // el proyecto se creó; el error se mostrará al navegar a él
      }
    }
  }

  const handleAdvance = async (task: TaskOut) => {
    setAdvancingId(task.id)
    try {
      const next: TaskStatus =
        task.status === 'todo' ? 'in_progress' : 'done'
      await api.updateTask(task.id, { status: next })
      await load()
    } catch (err) {
      if (err instanceof ApiError) onShowError(err.message)
    } finally {
      setAdvancingId(null)
    }
  }

  const handleInactivate = async () => {
    try {
      await api.inactivateProject(project.id)
      setConfirmInactive(false)
      onProjectStatusChanged()
    } catch (err) {
      setConfirmInactive(false)
      if (err instanceof ApiError) onShowError(err.message)
    }
  }

  const handleReactivate = async () => {
    try {
      await api.updateProject(project.id, { status: 'active' })
      onProjectStatusChanged()
    } catch (err) {
      if (err instanceof ApiError) onShowError(err.message)
    }
  }

  return (
    <section className="project-view">
      <header className="project-head">
        <div>
          <h1 className="project-title">{project.name}</h1>
          {project.description && (
            <p className="project-desc">{project.description}</p>
          )}
          <div className="project-head-meta">
            <ProgressBar value={project.done} total={project.total} />
            <span className="project-stats">
              {project.done} de {project.total} tareas completadas
            </span>
          </div>
        </div>
        <div className="project-head-actions">
          <Button variant="primary" onClick={() => setFormOpen(true)}>
            <PlusIcon />
            Nueva tarea
          </Button>
          {project.status === 'active' ? (
            <Button variant="quiet" onClick={() => setConfirmInactive(true)}>
              Inactivar proyecto
            </Button>
          ) : (
            <Button variant="ghost" onClick={handleReactivate}>
              Reactivar proyecto
            </Button>
          )}
        </div>
      </header>

      <div className="task-toolbar">
        <Select
          options={[
            { value: '', label: 'Estado: todos' },
            { value: 'todo', label: 'Por hacer' },
            { value: 'in_progress', label: 'En curso' },
            { value: 'done', label: 'Completadas' },
          ]}
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value as TaskStatus | '')}
          aria-label="Filtrar por estado"
        />
        <Select
          options={[
            { value: '', label: 'Prioridad: todas' },
            { value: 'low', label: 'Baja' },
            { value: 'medium', label: 'Media' },
            { value: 'high', label: 'Alta' },
          ]}
          value={filterPriority}
          onChange={(e) => setFilterPriority(e.target.value as Priority | '')}
          aria-label="Filtrar por prioridad"
        />
        <Select
          options={[
            { value: 'priority', label: 'Ordenar por prioridad' },
            { value: 'due_date', label: 'Ordenar por fecha límite' },
          ]}
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as 'priority' | 'due_date')}
          aria-label="Criterio de orden"
        />
        <Button
          variant="ghost"
          onClick={() => setOrder(order === 'asc' ? 'desc' : 'asc')}
        >
          {order === 'asc' ? 'Ascendente' : 'Descendente'}
        </Button>
      </div>

      {loading ? (
        <Spinner />
      ) : tasks.length === 0 ? (
        <EmptyState
          title={total === 0 ? 'Todavía no hay tareas' : 'Sin resultados'}
          message={
            total === 0
              ? 'Crea la primera tarea de este proyecto.'
              : 'Ninguna tarea coincide con los filtros.'
          }
          action={
            total === 0 ? (
              <Button variant="primary" onClick={() => setFormOpen(true)}>
                <PlusIcon />
                Crear tarea
              </Button>
            ) : undefined
          }
        />
      ) : (
        <ul className="task-list">
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              busy={advancingId === task.id}
              onAdvance={handleAdvance}
              onEdit={(t) => {
                setEditing(t)
                setFormOpen(true)
              }}
            />
          ))}
        </ul>
      )}

      {total > PAGE_SIZE && (
        <div className="pagination">
          <Button variant="quiet" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            ← Anterior
          </Button>
          <span className="pagination-info">
            Página {page} de {totalPages}
          </span>
          <Button
            variant="quiet"
            disabled={page >= totalPages}
            onClick={() => setPage(page + 1)}
          >
            Siguiente →
          </Button>
        </div>
      )}

      {formOpen && (
        <Modal title={editing ? 'Editar tarea' : 'Nueva tarea'} onClose={closeForm}>
          <TaskForm initial={editing ?? undefined} onSave={handleSave} onCancel={closeForm} />
        </Modal>
      )}

      {missingDraft && (
        <ProjectMissingModal
          projectName={project.name}
          onCreated={handleMissingProjectCreated}
          onClose={() => setMissingDraft(null)}
        />
      )}

      {confirmInactive && (
        <Modal title="Inactivar proyecto" onClose={() => setConfirmInactive(false)}>
          <p>
            El proyecto <strong>«{project.name}»</strong> dejará de estar activo. Solo se
            puede inactivar si todas sus tareas están completadas.
          </p>
          <div className="modal-actions">
            <Button onClick={() => setConfirmInactive(false)}>Cancelar</Button>
            <Button variant="danger" onClick={handleInactivate}>
              Inactivar
            </Button>
          </div>
        </Modal>
      )}
    </section>
  )
}
