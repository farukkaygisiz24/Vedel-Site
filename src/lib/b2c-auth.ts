export type B2CUser = {
  id: number
  username: string
  email: string
  phone: string
}

const TOKEN_KEY = 'vedel_b2c_token'
const API = '/api/b2c'

export function getToken() {
  if (typeof window === 'undefined') return null
  return window.localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string | null) {
  if (typeof window === 'undefined') return
  if (token) window.localStorage.setItem(TOKEN_KEY, token)
  else window.localStorage.removeItem(TOKEN_KEY)
}

type ApiError = { error?: string }

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> | undefined),
  }
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${API}${path}`, { ...options, headers })
  const data = (await res.json().catch(() => ({}))) as T & ApiError
  if (!res.ok) {
    throw new Error(data.error || 'İşlem başarısız.')
  }
  return data
}

export async function loginRequest(username: string, password: string) {
  const data = await request<{ token: string; user: B2CUser }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
  setToken(data.token)
  return data.user
}

export async function registerRequest(input: {
  username: string
  password: string
  password_confirm: string
}) {
  const data = await request<{ token: string; user: B2CUser }>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  setToken(data.token)
  return data.user
}

export async function meRequest() {
  const data = await request<{ user: B2CUser }>('/auth/me')
  return data.user
}

export async function logoutRequest() {
  try {
    await request('/auth/logout', { method: 'POST' })
  } finally {
    setToken(null)
  }
}
