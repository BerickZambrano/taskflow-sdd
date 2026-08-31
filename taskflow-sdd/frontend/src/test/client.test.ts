import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest'

import { api, ApiError, getToken, setToken } from '../api/client'

const fetchMock = vi.fn()

function jsonResponse(status: number, body: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response
}

beforeAll(() => {
  vi.stubGlobal('fetch', fetchMock)
})

afterEach(() => {
  fetchMock.mockReset()
  localStorage.clear()
})

describe('api client', () => {
  it('hace login y devuelve el token', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(200, { access_token: 'abc', token_type: 'bearer' }),
    )

    const result = await api.login('alice', 'clave')

    expect(result.access_token).toBe('abc')
    expect(fetchMock).toHaveBeenCalledWith(
      '/auth/login',
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('traduce un error 404 al mensaje en español de la API', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(404, { detail: 'El proyecto no existe.' }),
    )

    const promise = api.createTask('p1', {
      title: 'x',
      description: null,
      priority: 'medium',
      due_date: null,
    })

    await expect(promise).rejects.toMatchObject({
      status: 404,
      message: 'El proyecto no existe.',
    })
  })

  it('usa un mensaje genérico en español si el cuerpo no es JSON', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(500, { not: 'json' }),
    )

    await expect(api.listProjects()).rejects.toMatchObject({
      status: 500,
      message: 'Ocurrió un error inesperado.',
    })
  })

  it('al recibir 401 limpia el token y emite evento de sesión expirada', async () => {
    setToken('abc')
    const onUnauthorized = vi.fn()
    window.addEventListener('taskflow:unauthorized', onUnauthorized)
    fetchMock.mockResolvedValueOnce(jsonResponse(401, { detail: 'Sesión no válida' }))

    await expect(api.listProjects()).rejects.toBeInstanceOf(ApiError)

    expect(getToken()).toBeNull()
    expect(onUnauthorized).toHaveBeenCalled()
  })
})
