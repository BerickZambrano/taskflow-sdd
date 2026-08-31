import type { DragEvent } from 'react'

import type { TaskOut, TaskStatus } from '../api/types'
import { DueBadge, DueDate, PriorityMark, StatusChip, TagChip } from './ui'
import { ArrowRightIcon, CheckIcon, TimerIcon } from './icons'

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
  onLogTime: (task: TaskOut) => void
  onDragStart?: (event: DragEvent<HTMLLIElement>) => void
  onDragEnd?: (event: DragEvent<HTMLLIElement>) => void
  busy?: boolean
}

export function TaskCard({
  task,
  onAdvance,
  onEdit,
  onLogTime,
  onDragStart,
  onDragEnd,
  busy,
}: TaskCardProps) {
  const next = NEXT[task.status]
  const isDone = task.status === 'done'

  return (
    <li
      className={`task-card ${isDone ? 'done' : ''} ${busy ? 'dragging' : ''}`}
      draggable
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
    >
      <div className="task-main">
        <div className="task-title-line">
          <h3 className="task-title">{task.title}</h3>
          <DueBadge dueDate={task.due_date} completed={isDone} />
        </div>
        {task.description && <p className="task-desc">{task.description}</p>}
        {task.tags.length > 0 && (
          <div className="task-tags">
            {task.tags.map((tag) => (
              <TagChip key={tag.id} tag={tag} />
            ))}
          </div>
        )}
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
          className="icon-btn"
          onClick={() => onLogTime(task)}
          title="Registrar tiempo"
          aria-label="Registrar tiempo"
        >
          <TimerIcon />
        </button>
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
