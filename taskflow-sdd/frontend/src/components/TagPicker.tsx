import { useState } from 'react'

import { ApiError } from '../api/client'
import type { TagOut } from '../api/types'

interface TagPickerProps {
  tags: TagOut[]
  selected: string[]
  onChange: (selected: string[]) => void
  onCreate: (name: string) => Promise<TagOut>
  onError: (message: string) => void
}

export function TagPicker({ tags, selected, onChange, onCreate, onError }: TagPickerProps) {
  const [newName, setNewName] = useState('')
  const [busy, setBusy] = useState(false)

  const toggle = (id: string) => {
    onChange(selected.includes(id) ? selected.filter((s) => s !== id) : [...selected, id])
  }

  const create = async (event: React.FormEvent) => {
    event.preventDefault()
    const name = newName.trim()
    if (!name) return
    setBusy(true)
    try {
      const tag = await onCreate(name)
      onChange([...selected, tag.id])
      setNewName('')
    } catch (err) {
      if (err instanceof ApiError) onError(err.message)
      else onError('No se pudo crear la etiqueta.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="tag-picker">
      <span className="field-label">Etiquetas</span>
      <div className="tag-picker-list">
        {tags.map((tag) => {
          const active = selected.includes(tag.id)
          return (
            <button
              key={tag.id}
              type="button"
              className={`tag-pick ${active ? 'active' : ''}`}
              style={{ borderColor: tag.color, color: active ? tag.color : undefined }}
              onClick={() => toggle(tag.id)}
            >
              <span className="tag-pick-dot" style={{ background: tag.color }} />
              {tag.name}
            </button>
          )
        })}
        {tags.length === 0 && <span className="tag-picker-empty">Sin etiquetas aún</span>}
      </div>
      <form className="tag-picker-new" onSubmit={create}>
        <input
          className="input"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="Nueva etiqueta…"
        />
        <button type="submit" className="btn btn-ghost" disabled={busy || !newName.trim()}>
          Crear
        </button>
      </form>
    </div>
  )
}
