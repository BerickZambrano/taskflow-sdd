export type TaskStatus = 'todo' | 'in_progress' | 'done'
export type Priority = 'low' | 'medium' | 'high'
export type ProjectStatus = 'active' | 'inactive'
export interface UserOut {
  id: string
  username: string
  email: string
  created_at: string
}

export interface ProjectOut {
  id: string
  name: string
  description: string | null
  status: ProjectStatus
  created_at: string
  updated_at: string
}

export interface TaskOut {
  id: string
  title: string
  description: string | null
  priority: Priority
  status: TaskStatus
  due_date: string | null
  assignee_id: string | null
  project_id: string
  created_at: string
  updated_at: string
}

export interface TaskListOut {
  items: TaskOut[]
  total: number
  page: number
  page_size: number
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface TaskDraft {
  title: string
  description: string | null
  priority: Priority
  due_date: string | null
}

export interface TaskListParams {
  status?: TaskStatus
  priority?: Priority
  sort_by?: 'priority' | 'due_date'
  order?: 'asc' | 'desc'
  page?: number
  page_size?: number
}
