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
  onTaskStatusChanged: (projectId: string) => void
  onShowError: (message: string) => void
}

const PAGE_SIZE = 100

const COLUMNS: { status: TaskStatus; title: string }[] = [
  { status: 'todo', title: 'Por hacer' },
  { status: 'in_progress', title: 'En curso' },
  { status: 'done', title: 'Completada' },
]

export function ProjectView({
  project,
  onProjectCreated,
  onProjectStatusChanged,
  onTaskStatusChanged,
  onShowError,
}: ProjectViewProps) {
  const [tasks, setTasks] = useState<TaskOut[]>([])
  const [loading, setLoading] = useState(true)

  const [filterPriority, setFilterPriority] = useState<Priority | ''>('')
  const [sortBy, setSortBy] = useState<'priority' | 'due_date'>('priority')
  const [order, setOrder] = useState<'asc' | 'desc'>('asc')

  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<TaskOut | null>(null)
  const [missingDraft, setMissingDraft] = useState<TaskDraft | null>(null)
  const [confirmInactive, setConfirmInactive] = useState(false)
  const [draggingId, setDraggingId] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api.listTasks(project.id, {
        priority: filterPriority || undefined,
        sort_by: sortBy,
        order,
        page: 1,
        page_size: PAGE_SIZE,
      })
      setTasks(data.items)
    } catch (err) {
      if (err instanceof ApiError) onShowError(err.message)
    } finally {
      setLoading(false)
    }
  }, [project.id, filterPriority, sortBy, order, onShowError])

  useEffect(() => {
    load()
  }, [load])

  const columns = useMemo(() => {
    const byStatus: Record<TaskStatus, TaskOut[]> = {
      todo: [],
      in_progress: [],
      done: [],
    }
    for (const task of tasks) byStatus[task.status].push(task)
    return byStatus
  }, [tasks])

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
        onTaskStatusChanged(project.id)
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

  const moveTask = async (taskId: string, target: TaskStatus) => {
    const task = tasks.find((t) => t.id === taskId)
    if (!task || task.status === target) return
    try {
      const updated = await api.updateTask(taskId, { status: target })
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)))
      onTaskStatusChanged(project.id)
    } catch (err) {
      if (err instanceof ApiError) onShowError(err.message)
    } finally {
      setDraggingId(null)
    }
  }

  const handleAdvance = async (task: TaskOut) => {
    const next: TaskStatus = task.status === 'todo' ? 'in_progress' : 'done'
    await moveTask(task.id, next)
  }

  const handleDrop = (target: TaskStatus) => (event: React.DragEvent) => {
    event.preventDefault()
    const taskId = event.dataTransfer.getData('text/plain')
    if (taskId) moveTask(taskId, target)
    setDraggingId(null)
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
          title="Todavía no hay tareas"
          message="Crea la primera tarea de este proyecto."
          action={
            <Button variant="primary" onClick={() => setFormOpen(true)}>
              <PlusIcon />
              Crear tarea
            </Button>
          }
        />
      ) : (
        <div className="board">
          {COLUMNS.map((column) => (
            <div
              key={column.status}
              className={`board-column ${draggingId ? 'drop-target' : ''}`}
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop(column.status)}
            >
              <header className="board-column-head">
                <span className="board-column-title">{column.title}</span>
                <span className="board-column-count">
                  {columns[column.status].length}
                </span>
              </header>
              <ul className="board-column-body">
                {columns[column.status].map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    busy={draggingId === task.id}
                    onAdvance={handleAdvance}
                    onEdit={(t) => {
                      setEditing(t)
                      setFormOpen(true)
                    }}
                    onDragStart={(event) => {
                      setDraggingId(task.id)
                      event.dataTransfer.setData('text/plain', task.id)
                      event.dataTransfer.effectAllowed = 'move'
                    }}
                    onDragEnd={() => setDraggingId(null)}
                  />
                ))}
                {columns[column.status].length === 0 && (
                  <li className="board-empty">Suelta aquí una tarea</li>
                )}
              </ul>
            </div>
          ))}
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
