import type { TaskOut } from '../api/types'

export type DueState = 'overdue' | 'due_soon' | 'ok' | null

const SOON_DAYS = 3

type DueInput = Pick<TaskOut, 'due_date' | 'status' | 'completed_at'>

export function dueState(task: DueInput): DueState {
  if (!task.due_date || task.status === 'done' || task.completed_at) return null
  const today = new Date()
  const todayMid = new Date(today.getFullYear(), today.getMonth(), today.getDate())
  const due = new Date(`${task.due_date}T00:00:00`)
  const diffDays = Math.round((due.getTime() - todayMid.getTime()) / 86400000)
  if (diffDays < 0) return 'overdue'
  if (diffDays <= SOON_DAYS) return 'due_soon'
  return 'ok'
}

export function dueStateLabel(state: DueState): string {
  if (state === 'overdue') return 'Vencida'
  if (state === 'due_soon') return 'Próxima'
  return ''
}

export function formatMinutes(minutes: number): string {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (h === 0) return `${m}m`
  if (m === 0) return `${h}h`
  return `${h}h ${m}m`
}
