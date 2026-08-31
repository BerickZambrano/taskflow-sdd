import { useCallback, useEffect, useState } from 'react'

import { api, clearToken, getToken, setToken } from './api/client'
import type { ProjectOut } from './api/types'
import { AppShell } from './components/AppShell'
import { AuthPage } from './components/AuthPage'
import type { ProjectWithStats } from './components/Sidebar'

const USERNAME_KEY = 'taskflow_username'
const THEME_KEY = 'taskflow_theme'

type Theme = 'light' | 'dark'

function initialTheme(): Theme {
  return localStorage.getItem(THEME_KEY) === 'dark' ? 'dark' : 'light'
}

export default function App() {
  const [token, setTokenState] = useState<string | null>(() => getToken())
  const [username, setUsername] = useState(() => localStorage.getItem(USERNAME_KEY) ?? '')
  const [theme, setTheme] = useState<Theme>(initialTheme)
  const [projects, setProjects] = useState<ProjectWithStats[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const handleLogout = useCallback(() => {
    clearToken()
    localStorage.removeItem(USERNAME_KEY)
    setTokenState(null)
    setProjects([])
    setSelectedId(null)
  }, [])

  const loadProjects = useCallback(async () => {
    const list = await api.listProjects()
    const withStats = await Promise.all(
      list.map(async (project) => {
        const all = await api.listTasks(project.id, { page_size: 1 })
        const done = await api.listTasks(project.id, { status: 'done', page_size: 1 })
        return { ...project, total: all.total, done: done.total }
      }),
    )
    setProjects(withStats)
    return withStats
  }, [])

  useEffect(() => {
    if (!token) return
    loadProjects()
      .then((list) => setSelectedId((current) => current ?? list[0]?.id ?? null))
      .catch(() => handleLogout())
  }, [token, loadProjects, handleLogout])

  useEffect(() => {
    const onUnauthorized = () => handleLogout()
    window.addEventListener('taskflow:unauthorized', onUnauthorized)
    return () => window.removeEventListener('taskflow:unauthorized', onUnauthorized)
  }, [handleLogout])

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem(THEME_KEY, theme)
  }, [theme])

  const handleAuthed = (newToken: string, newUsername: string) => {
    setToken(newToken)
    localStorage.setItem(USERNAME_KEY, newUsername)
    setUsername(newUsername)
    setTokenState(newToken)
    setProjects([])
    setSelectedId(null)
  }

  const handleProjectCreated = (project: ProjectOut) => {
    setProjects((current) => [{ ...project, done: 0, total: 0 }, ...current])
    setSelectedId(project.id)
    api
      .listTasks(project.id, { page_size: 1 })
      .then((data) => setProjects((current) => current.map((p) => (p.id === project.id ? { ...p, total: data.total } : p))))
      .catch(() => undefined)
  }

  const handleProjectStatusChanged = () => {
    loadProjects().catch(() => undefined)
  }

  const handleTaskStatusChanged = useCallback(async (projectId: string) => {
    const all = await api.listTasks(projectId, { page_size: 1 })
    const done = await api.listTasks(projectId, { status: 'done', page_size: 1 })
    setProjects((current) =>
      current.map((p) =>
        p.id === projectId ? { ...p, total: all.total, done: done.total } : p,
      ),
    )
  }, [])

  if (!token) {
    return <AuthPage onAuthed={handleAuthed} />
  }

  return (
    <AppShell
      projects={projects}
      selectedId={selectedId}
      username={username || 'usuario'}
      theme={theme}
      onSelectProject={setSelectedId}
      onProjectCreated={handleProjectCreated}
      onProjectStatusChanged={handleProjectStatusChanged}
      onTaskStatusChanged={handleTaskStatusChanged}
      onToggleTheme={() => setTheme((t) => (t === 'light' ? 'dark' : 'light'))}
      onLogout={handleLogout}
    />
  )
}
