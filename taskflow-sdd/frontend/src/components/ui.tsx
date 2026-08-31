import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from 'react'

import type { Priority, TaskStatus } from '../api/types'
import { CalendarIcon } from './icons'

type ButtonVariant = 'primary' | 'ghost' | 'quiet' | 'danger'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
}

export function Button({ variant = 'ghost', className = '', ...props }: ButtonProps) {
  return <button className={`btn btn-${variant} ${className}`} {...props} />
}

interface FieldProps {
  label: string
  children: ReactNode
}

export function Field({ label, children }: FieldProps) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
    </label>
  )
}

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input className="input" {...props} />
}

export function TextArea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className="textarea" {...props} />
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  options: { value: string; label: string }[]
}

export function Select({ options, ...props }: SelectProps) {
  return (
    <select className="select" {...props}>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  )
}

export function StatusChip({ status }: { status: TaskStatus }) {
  const labels: Record<TaskStatus, string> = {
    todo: 'Por hacer',
    in_progress: 'En curso',
    done: 'Completada',
  }
  return (
    <span className={`chip chip-${status}`}>
      <span className="dot" />
      {labels[status]}
    </span>
  )
}

export function PriorityMark({ priority, withLabel = true }: { priority: Priority; withLabel?: boolean }) {
  const labels: Record<Priority, string> = {
    low: 'Baja',
    medium: 'Media',
    high: 'Alta',
  }
  return (
    <span className={`priority ${priority}`} title={`Prioridad ${labels[priority].toLowerCase()}`}>
      <span className="bar" />
      <span className="bar" />
      <span className="bar" />
      {withLabel && <span className="label">{labels[priority]}</span>}
    </span>
  )
}

export function ProgressBar({ value, total }: { value: number; total: number }) {
  const percent = total === 0 ? 0 : Math.round((value / total) * 100)
  return (
    <div className="progress" role="progressbar" aria-valuenow={percent} aria-valuemin={0} aria-valuemax={100}>
      <div style={{ width: `${percent}%` }} />
    </div>
  )
}

export function DueDate({ dueDate }: { dueDate: string | null }) {
  if (!dueDate) return null
  return (
    <span className="due-date">
      <CalendarIcon />
      {dueDate}
    </span>
  )
}

export function Spinner() {
  return <div className="spinner" role="status" aria-label="Cargando" />
}

export function EmptyState({ title, message, action }: { title: string; message: string; action?: ReactNode }) {
  return (
    <div className="empty">
      <div className="empty-title">{title}</div>
      <p>{message}</p>
      {action && <div style={{ marginTop: 16 }}>{action}</div>}
    </div>
  )
}
