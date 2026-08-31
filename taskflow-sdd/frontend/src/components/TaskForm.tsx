import { useState } from 'react'

import { ApiError } from '../api/client'
import type { Priority, TagOut, TaskDraft, TaskOut } from '../api/types'
import { Button, Field, Select, TextArea, TextInput } from './ui'
import { TagPicker } from './TagPicker'

interface TaskFormProps {
  initial?: TaskOut
  tags: TagOut[]
  onSave: (draft: TaskDraft, tagIds: string[]) => Promise<void>
  onCreateTag: (name: string) => Promise<TagOut>
  onError: (message: string) => void
  onCancel: () => void
}

const emptyDraft: TaskDraft = {
  title: '',
  description: null,
  priority: 'medium',
  due_date: null,
}

export function TaskForm({ initial, tags, onSave, onCreateTag, onError, onCancel }: TaskFormProps) {
  const [draft, setDraft] = useState<TaskDraft>(
    initial
      ? {
          title: initial.title,
          description: initial.description,
          priority: initial.priority,
          due_date: initial.due_date,
        }
      : emptyDraft,
  )
  const [tagIds, setTagIds] = useState<string[]>(initial?.tags.map((t) => t.id) ?? [])
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const submit = async (event: React.FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await onSave(
        {
          ...draft,
          title: draft.title.trim(),
          description: draft.description?.trim() || null,
          due_date: draft.due_date || null,
        },
        tagIds,
      )
    } catch (err) {
      if (err instanceof ApiError) setError(err.message)
      else setError('No se pudo conectar con el servidor.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={submit}>
      {error && <p className="form-error">{error}</p>}
      <Field label="Título">
        <TextInput
          value={draft.title}
          onChange={(e) => setDraft({ ...draft, title: e.target.value })}
          placeholder="¿Qué hay que hacer?"
          autoFocus
          required
        />
      </Field>
      <Field label="Descripción (opcional)">
        <TextArea
          value={draft.description ?? ''}
          onChange={(e) => setDraft({ ...draft, description: e.target.value })}
          placeholder="Algún detalle útil"
        />
      </Field>
      <div className="row">
        <Field label="Prioridad">
          <Select
            options={[
              { value: 'low', label: 'Baja' },
              { value: 'medium', label: 'Media' },
              { value: 'high', label: 'Alta' },
            ]}
            value={draft.priority}
            onChange={(e) => setDraft({ ...draft, priority: e.target.value as Priority })}
          />
        </Field>
        <Field label="Fecha límite (opcional)">
          <TextInput
            type="date"
            value={draft.due_date ?? ''}
            onChange={(e) => setDraft({ ...draft, due_date: e.target.value })}
          />
        </Field>
      </div>
      <div style={{ margin: '10px 0' }}>
        <TagPicker
          tags={tags}
          selected={tagIds}
          onChange={setTagIds}
          onCreate={onCreateTag}
          onError={onError}
        />
      </div>
      <div className="modal-actions">
        <Button type="button" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" variant="primary" disabled={busy || draft.title.trim() === ''}>
          {busy ? 'Guardando…' : initial ? 'Guardar cambios' : 'Crear tarea'}
        </Button>
      </div>
    </form>
  )
}
