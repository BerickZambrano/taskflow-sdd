import { useState } from 'react'

import { api, ApiError, setToken } from '../api/client'
import { Button, Field, TextInput } from './ui'
import { LogoMark } from './icons'

interface AuthPageProps {
  onAuthed: (token: string, username: string) => void
}

type Mode = 'login' | 'register'

export function AuthPage({ onAuthed }: AuthPageProps) {
  const [mode, setMode] = useState<Mode>('login')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const switchMode = (next: Mode) => {
    setMode(next)
    setError(null)
  }

  const submit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError(null)
    setBusy(true)
    try {
      if (mode === 'register') {
        const user = await api.register(username.trim(), email.trim(), password)
        const login = await api.login(user.username, password)
        setToken(login.access_token)
        onAuthed(login.access_token, user.username)
      } else {
        const login = await api.login(username.trim(), password)
        setToken(login.access_token)
        onAuthed(login.access_token, username.trim())
      }
    } catch (err) {
      if (err instanceof ApiError) setError(err.message)
      else setError('No se pudo conectar con el servidor.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-brand">
        <div className="auth-brand-inner">
          <div className="auth-logo">
            <LogoMark size={30} />
            <span className="auth-wordmark">TaskFlow</span>
          </div>
          <p className="auth-tagline">
            Organiza tu trabajo con calma.
            <br />
            Proyectos claros, tareas al día.
          </p>
          <p className="auth-note">
            Una herramienta sencilla para llevar el hilo de tus proyectos sin perder el
            detalle.
          </p>
        </div>
      </div>

      <div className="auth-form-side">
        <form className="auth-card card" onSubmit={submit}>
          <div className="auth-tabs">
            <button
              type="button"
              className={mode === 'login' ? 'auth-tab active' : 'auth-tab'}
              onClick={() => switchMode('login')}
            >
              Iniciar sesión
            </button>
            <button
              type="button"
              className={mode === 'register' ? 'auth-tab active' : 'auth-tab'}
              onClick={() => switchMode('register')}
            >
              Crear cuenta
            </button>
          </div>

          <h1 className="auth-title">
            {mode === 'login' ? 'Hola de nuevo' : 'Empecemos'}
          </h1>

          {error && <p className="form-error">{error}</p>}

          {mode === 'register' && (
            <Field label="Correo electrónico">
              <TextInput
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tu@correo.com"
                autoComplete="email"
              />
            </Field>
          )}

          <Field label="Usuario o correo">
            <TextInput
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={mode === 'register' ? 'Elige un usuario' : 'usuario o correo'}
              autoComplete="username"
            />
          </Field>

          <Field label="Contraseña">
            <TextInput
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
            />
          </Field>

          <Button type="submit" variant="primary" className="btn-block" disabled={busy}>
            {busy ? 'Un momento…' : mode === 'login' ? 'Entrar' : 'Registrarme'}
          </Button>
        </form>
      </div>
    </div>
  )
}
