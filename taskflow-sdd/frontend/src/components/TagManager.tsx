import { useState } from 'react'

import { api, ApiError } from '../api/client'
import type { TagOut } from '../api/types'
import { Modal } from './Modal'
import { Button, TextInput } from './ui'

interface TagManagerProps {
  initialTags: TagOut[]
  onCreated: (tag: TagOut) => void
  onDeleted: (tagId: string) => void
  onClose: () => void
}

export function TagManager({ initialTags, onCreated, onDeleted, onClose }: TagManagerProps) {
  const [tags, setTags] = useState(initialTags)
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)

  const create = async (event: React.FormEvent) => {
    event.preventDefault()
    setError(null)
    try {
      const tag = await api.createTag(name.trim())
      setTags((current) => [...current, tag])
      onCreated(tag)
      setName('')
    } catch (err) {
      if (err instanceof ApiError) setError(err.message)
      else setError('No se pudo crear la etiqueta.')
    }
  }

  const remove = async (tag: TagOut) => {
    try {
      await api.deleteTag(tag.id)
      setTags((current) => current.filter((t) => t.id !== tag.id))
      onDeleted(tag.id)
    } catch (err) {
      if (err instanceof ApiError) setError(err.message)
    }
  }

  return (
    <Modal title="Etiquetas" onClose={onClose}>
      {error && <p className="form-error">{error}</p>}
      <ul className="tag-list">
        {tags.map((tag) => (
          <li key={tag.id} className="tag-list-item">
            <span className="tag-list-dot" style={{ background: tag.color }} />
            <span className="tag-list-name">{tag.name}</span>
            <button className="btn btn-quiet" onClick={() => remove(tag)}>
              Eliminar
            </button>
          </li>
        ))}
        {tags.length === 0 && <li className="tag-list-empty">No hay etiquetas todavía.</li>}
      </ul>
      <form className="tag-picker-new" onSubmit={create}>
        <TextInput value={name} onChange={(e) => setName(e.target.value)} placeholder="Nueva etiqueta…" />
        <Button type="submit" variant="primary" disabled={!name.trim()}>
          Crear
        </Button>
      </form>
    </Modal>
  )
}
