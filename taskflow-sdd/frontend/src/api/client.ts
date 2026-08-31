import type {
  LoginResponse,
  ProjectOut,
  StatsOut,
  TagOut,
  TaskDraft,
  TaskListOut,
  TaskListParams,
  TaskOut,
  TimeEntryOut,
  UserOut,
} from './types'

const TOKEN_KEY = 'taskflow_token'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  const response = await fetch(path, { ...options, headers })

  if (response.status === 401) {
    clearToken()
    window.dispatchEvent(new Event('taskflow:unauthorized'))
  }

  if (!response.ok) {
    let detail = 'Ocurrió un error inesperado.'
    try {
      const body = await response.json()
      if (typeof body.detail === 'string') detail = body.detail
    } catch {
      // keep default message
    }
    throw new ApiError(response.status, detail)
  }

  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

const json = (method: string, body: unknown): RequestInit => ({
  method,
  body: JSON.stringify(body),
})

export const api = {
  async register(username: string, email: string, password: string): Promise<UserOut> {
    return request('/auth/register', json('POST', { username, email, password }))
  },

  async login(identifier: string, password: string): Promise<LoginResponse> {
    return request('/auth/login', json('POST', { identifier, password }))
  },

  async listProjects(): Promise<ProjectOut[]> {
    return request('/projects')
  },

  async createProject(name: string, description: string | null): Promise<ProjectOut> {
    return request('/projects', json('POST', { name, description }))
  },

  async getProject(id: string): Promise<ProjectOut> {
    return request(`/projects/${id}`)
  },

  async updateProject(
    id: string,
    patch: Partial<Pick<ProjectOut, 'name' | 'description' | 'status'>>,
  ): Promise<ProjectOut> {
    return request(`/projects/${id}`, json('PATCH', patch))
  },

  async inactivateProject(id: string): Promise<void> {
    return request(`/projects/${id}`, { method: 'DELETE' })
  },

  async listTasks(projectId: string, params: TaskListParams = {}): Promise<TaskListOut> {
    const query = new URLSearchParams()
    if (params.status) query.set('status', params.status)
    if (params.priority) query.set('priority', params.priority)
    if (params.tag_id) query.set('tag_id', params.tag_id)
    if (params.sort_by) query.set('sort_by', params.sort_by)
    if (params.order) query.set('order', params.order)
    if (params.page) query.set('page', String(params.page))
    if (params.page_size) query.set('page_size', String(params.page_size))
    const qs = query.toString()
    return request(`/projects/${projectId}/tasks${qs ? `?${qs}` : ''}`)
  },

  async createTask(projectId: string, draft: TaskDraft): Promise<TaskOut> {
    return request(`/projects/${projectId}/tasks`, json('POST', draft))
  },

  async updateTask(id: string, patch: Partial<TaskOut>): Promise<TaskOut> {
    return request(`/tasks/${id}`, json('PATCH', patch))
  },

  async deleteTask(id: string): Promise<void> {
    return request(`/tasks/${id}`, { method: 'DELETE' })
  },

  async listTags(): Promise<TagOut[]> {
    return request('/tags')
  },

  async createTag(name: string): Promise<TagOut> {
    return request('/tags', json('POST', { name }))
  },

  async deleteTag(id: string): Promise<void> {
    return request(`/tags/${id}`, { method: 'DELETE' })
  },

  async assignTag(taskId: string, tagId: string): Promise<TagOut> {
    return request(`/tasks/${taskId}/tags`, json('POST', { tag_id: tagId }))
  },

  async removeTag(taskId: string, tagId: string): Promise<TaskOut> {
    return request(`/tasks/${taskId}/tags/${tagId}`, { method: 'DELETE' })
  },

  async createTimeEntry(payload: {
    task_id?: string | null
    minutes: number
    entry_date?: string | null
  }): Promise<TimeEntryOut> {
    return request('/time-entries', json('POST', payload))
  },

  async getStats(): Promise<StatsOut> {
    return request('/stats')
  },
}
