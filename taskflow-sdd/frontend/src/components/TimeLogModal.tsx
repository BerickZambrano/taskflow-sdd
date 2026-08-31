import { useState } from 'react'

import { api, ApiError } from '../api/client'
import type { TaskOut } from '../api/types'
import { Modal } from './Modal'
import { Button, Field, TextInput } from './ui'

interface TimeLogModalProps {
  task: TaskOut
  onSaved: () => void
  onClose: () => void
}

export function TimeLogModal({ task, onSaved, onClose }: TimeLogModalProps) {
  const [minutes, setMinutes] = useState('25')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const save = async (event: React.FormEvent) => {
    event.preventDefault()
    const value = Number(minutes)
    if (!Number.isFinite(value) || value <= 0) {
      setError('Introduce los minutos.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      await api.createTimeEntry({ task_id: task.id, minutes: value })
      onSaved()
    } catch (err) {
      if (err instanceof ApiError) setError(err.message)
      else setError('No se pudo guardar el tiempo.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Modal title="Registrar tiempo" onClose={onClose}>
      <p>
        Tiempo dedicado a <strong>«{task.title}»</strong>.
      </p>
      {error && <p className="form-error">{error}</p>}
      <form onSubmit={save}>
        <Field label="Minutos">
          <TextInput
            type="number"
            min={1}
            max={1440}
            value={minutes}
            onChange={(e) => setMinutes(e.target.value)}
          />
        </Field>
        <div className="modal-actions">
          <Button type="button" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" disabled={busy}>
            {busy ? 'Guardando…' : 'Guardar'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
