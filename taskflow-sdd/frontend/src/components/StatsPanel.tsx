import { useEffect, useState } from 'react'

import { api, ApiError } from '../api/client'
import type { StatsOut } from '../api/types'
import { formatMinutes } from '../lib/taskUtils'
import { Modal } from './Modal'
import { Spinner } from './ui'

interface StatsPanelProps {
  onClose: () => void
}

export function StatsPanel({ onClose }: StatsPanelProps) {
  const [stats, setStats] = useState<StatsOut | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getStats()
      .then(setStats)
      .catch((err) => setError(err instanceof ApiError ? err.message : 'No se pudo cargar.'))
  }, [])

  const maxDay = stats ? Math.max(1, ...stats.minutes_by_day.map((d) => d.minutes)) : 1

  return (
    <Modal title="Estadísticas" onClose={onClose}>
      {error && <p className="form-error">{error}</p>}
      {!stats ? (
        <Spinner />
      ) : (
        <div className="stats">
          <div className="stats-cards">
            <div className="stat-card">
              <span className="stat-value">{stats.streak}</span>
              <span className="stat-label">días de racha</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{stats.days_studied}</span>
              <span className="stat-label">días con tiempo</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{formatMinutes(stats.minutes_total)}</span>
              <span className="stat-label">tiempo total</span>
            </div>
          </div>

          <div className="stat-section">
            <h4>Tiempo por día</h4>
            {stats.minutes_by_day.length === 0 ? (
              <p className="stat-empty">Aún sin tiempo registrado.</p>
            ) : (
              <ul className="stat-bars">
                {stats.minutes_by_day.map((d) => (
                  <li key={d.date}>
                    <span className="stat-bar-label">{d.date}</span>
                    <div className="stat-bar">
                      <div style={{ width: `${(d.minutes / maxDay) * 100}%` }} />
                    </div>
                    <span className="stat-bar-value">{formatMinutes(d.minutes)}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="stat-section">
            <h4>Por etiqueta</h4>
            {stats.minutes_by_tag.length === 0 ? (
              <p className="stat-empty">Sin datos por etiqueta.</p>
            ) : (
              <ul className="stat-list">
                {stats.minutes_by_tag.map((t) => (
                  <li key={t.tag_id}>
                    <span>{t.name}</span>
                    <span className="stat-list-value">{formatMinutes(t.minutes)}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </Modal>
  )
}
