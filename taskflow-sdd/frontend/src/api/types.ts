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

export interface TagOut {
  id: string
  name: string
  color: string
  created_at: string
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
  completed_at: string | null
  tags: TagOut[]
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
  tag_id?: string
  sort_by?: 'priority' | 'due_date'
  order?: 'asc' | 'desc'
  page?: number
  page_size?: number
}

export interface TimeEntryOut {
  id: string
  task_id: string | null
  minutes: number
  entry_date: string
  created_at: string
}

export interface StatsOut {
  streak: number
  days_studied: number
  tasks_completed: number
  minutes_total: number
  minutes_by_day: { date: string; minutes: number }[]
  minutes_by_tag: { tag_id: string; name: string; minutes: number }[]
  minutes_by_project: { project_id: string; name: string; minutes: number }[]
}
