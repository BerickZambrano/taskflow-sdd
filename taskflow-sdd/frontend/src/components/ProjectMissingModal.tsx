import { Modal } from './Modal'
import { ProjectForm } from './ProjectForm'
import type { ProjectOut } from '../api/types'

interface ProjectMissingModalProps {
  projectName: string
  onCreated: (project: ProjectOut) => void
  onClose: () => void
}

export function ProjectMissingModal({ projectName, onCreated, onClose }: ProjectMissingModalProps) {
  return (
    <Modal title="El proyecto ya no existe" onClose={onClose}>
      <p>
        El proyecto <strong>«{projectName}»</strong> no está disponible. ¿Quieres crearlo y
        continuar con la tarea?
      </p>
      <ProjectForm
        initialName={projectName}
        submitLabel="Crear y continuar"
        onCreated={(project) => onCreated(project)}
        onCancel={onClose}
      />
    </Modal>
  )
}
