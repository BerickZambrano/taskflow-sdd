import { useState } from 'react'

import { api, ApiError } from '../api/client'
import type { ProjectOut } from '../api/types'
import { Button, Field, TextArea, TextInput } from './ui'

interface ProjectFormProps {
  onCreated: (project: ProjectOut) => void
  initialName?: string
  submitLabel?: string
  title?: string
  onCancel?: () => void
  inline?: boolean
}

export function ProjectForm({
  onCreated,
  initialName = '',
  submitLabel = 'Crear proyecto',
  onCancel,
  inline = true,
}: ProjectFormProps) {
  const [name, setName] = useState(initialName)
  const [description, setDescription] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const submit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError(null)
    setBusy(true)
    try {
      const project = await api.createProject(name.trim(), description.trim() || null)
      onCreated(project)
    } catch (err) {
      if (err instanceof ApiError) setError(err.message)
      else setError('No se pudo conectar con el servidor.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={submit} className={inline ? 'project-form' : ''}>
      {error && <p className="form-error">{error}</p>}
      <Field label="Nombre">
        <TextInput
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nombre del proyecto"
          autoFocus
          required
        />
      </Field>
      <Field label="Descripción (opcional)">
        <TextArea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="¿De qué trata?"
        />
      </Field>
      <div className="modal-actions">
        {onCancel && (
          <Button type="button" onClick={onCancel}>
            Cancelar
          </Button>
        )}
        <Button type="submit" variant="primary" disabled={busy || name.trim() === ''}>
          {busy ? 'Un momento…' : submitLabel}
        </Button>
      </div>
    </form>
  )
}
