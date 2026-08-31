import type { TaskOut, TaskStatus } from '../api/types'
import { DueDate, PriorityMark, StatusChip } from './ui'
import { ArrowRightIcon, CheckIcon } from './icons'

const NEXT: Record<TaskStatus, TaskStatus | null> = {
  todo: 'in_progress',
  in_progress: 'done',
  done: null,
}

const NEXT_LABEL: Record<TaskStatus, string> = {
  todo: 'Empezar',
  in_progress: 'Marcar completada',
  done: '',
}

interface TaskCardProps {
  task: TaskOut
  onAdvance: (task: TaskOut) => void
  onEdit: (task: TaskOut) => void
  busy?: boolean
}

export function TaskCard({ task, onAdvance, onEdit, busy }: TaskCardProps) {
  const next = NEXT[task.status]
  const isDone = task.status === 'done'

  return (
    <li className={`task-card ${isDone ? 'done' : ''}`}>
      <div className="task-main">
        <h3 className="task-title">{task.title}</h3>
        {task.description && <p className="task-desc">{task.description}</p>}
        <div className="task-meta">
          <StatusChip status={task.status} />
          <PriorityMark priority={task.priority} />
          <DueDate dueDate={task.due_date} />
        </div>
      </div>
      <div className="task-actions">
        {!isDone && next && (
          <button
            className="btn btn-ghost task-advance"
            onClick={() => onAdvance(task)}
            disabled={busy}
          >
            {next === 'done' ? <CheckIcon /> : <ArrowRightIcon />}
            {NEXT_LABEL[task.status]}
          </button>
        )}
        <button
          className="btn btn-quiet"
          onClick={() => onEdit(task)}
          disabled={isDone}
          title={isDone ? 'No se puede modificar una tarea completada' : 'Editar tarea'}
        >
          Editar
        </button>
      </div>
    </li>
  )
}
