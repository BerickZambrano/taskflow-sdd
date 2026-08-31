import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { ProjectOut, TaskOut } from '../api/types'
import { ProjectMissingModal } from '../components/ProjectMissingModal'
import { ProjectForm } from '../components/ProjectForm'
import { TaskForm } from '../components/TaskForm'

const { createProject } = vi.hoisted(() => ({ createProject: vi.fn() }))

vi.mock('../api/client', () => {
  class ApiError extends Error {
    status: number
    constructor(status: number, message: string) {
      super(message)
      this.status = status
    }
  }
  return {
    api: { createProject },
    ApiError,
  }
})

beforeEach(() => {
  createProject.mockReset()
})

describe('ProjectForm', () => {
  it('crea un proyecto con nombre y descripción', async () => {
    createProject.mockResolvedValueOnce({ id: 'p1', name: 'Lanzamiento' } as ProjectOut)
    const onCreated = vi.fn()
    render(<ProjectForm onCreated={onCreated} />)

    fireEvent.change(screen.getByPlaceholderText('Nombre del proyecto'), {
      target: { value: 'Lanzamiento' },
    })
    fireEvent.change(screen.getByPlaceholderText('¿De qué trata?'), {
      target: { value: 'Sitio web' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Crear proyecto' }))

    await waitFor(() => expect(createProject).toHaveBeenCalledWith('Lanzamiento', 'Sitio web'))
    await waitFor(() => expect(onCreated).toHaveBeenCalled())
  })

  it('no envía si el nombre está vacío', () => {
    render(<ProjectForm onCreated={vi.fn()} />)
    const button = screen.getByRole('button', { name: 'Crear proyecto' })
    expect(button).toBeDisabled()
  })
})

describe('ProjectMissingModal', () => {
  it('ofrece crear el proyecto inexistente y continuar', async () => {
    createProject.mockResolvedValueOnce({ id: 'p9', name: 'Legado' } as ProjectOut)
    const onCreated = vi.fn()
    render(<ProjectMissingModal projectName="Legado" onCreated={onCreated} onClose={vi.fn()} />)

    expect(screen.getByText('El proyecto ya no existe')).toBeInTheDocument()
    expect(screen.getByText(/¿Quieres crearlo y continuar/)).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Crear y continuar' }))

    await waitFor(() => expect(createProject).toHaveBeenCalledWith('Legado', null))
    await waitFor(() => expect(onCreated).toHaveBeenCalledWith({ id: 'p9', name: 'Legado' }))
  })
})

describe('TaskForm', () => {
  it('muestra los valores iniciales al editar y guarda los cambios', async () => {
    const task: TaskOut = {
      id: 't1',
      title: 'Diseñar landing',
      description: 'En Figma',
      priority: 'high',
      status: 'in_progress',
      due_date: '2026-09-15',
      assignee_id: null,
      project_id: 'p1',
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    }
    const onSave = vi.fn().mockResolvedValue(undefined)
    render(<TaskForm initial={task} onSave={onSave} onCancel={vi.fn()} />)

    expect(screen.getByDisplayValue('Diseñar landing')).toBeInTheDocument()
    expect(screen.getByDisplayValue('2026-09-15')).toBeInTheDocument()

    fireEvent.change(screen.getByPlaceholderText('¿Qué hay que hacer?'), {
      target: { value: 'Nuevo título' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Guardar cambios' }))

    await waitFor(() =>
      expect(onSave).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Nuevo título', priority: 'high' }),
      ),
    )
  })
})
