import type { AuthUser, DashboardPayload } from '../types/dashboard'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

let inMemoryToken: string | null = null
let refreshPromise: Promise<string | null> | null = null

export function setAccessToken(token: string | null): void {
  inMemoryToken = token
}

export function getAccessToken(): string | null {
  return inMemoryToken
}

export async function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) {
    return refreshPromise
  }

  refreshPromise = (async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
      })
      if (!res.ok) {
        inMemoryToken = null
        return null
      }
      const data = await res.json()
      inMemoryToken = data.access_token || null
      return inMemoryToken
    } catch {
      inMemoryToken = null
      return null
    } finally {
      refreshPromise = null
    }
  })()

  return refreshPromise
}

export async function fetchApi<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${path}`
  const headers = new Headers(options.headers || {})

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  if (inMemoryToken && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${inMemoryToken}`)
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include',
  })

  if (response.status === 401) {
    // Attempt silent refresh once
    const newToken = await refreshAccessToken()
    if (newToken) {
      headers.set('Authorization', `Bearer ${newToken}`)
      const retryResponse = await fetch(url, {
        ...options,
        headers,
        credentials: 'include',
      })
      if (!retryResponse.ok) {
        const errJson = await retryResponse.json().catch(() => ({}))
        throw new Error(errJson?.detail?.error?.message || `API error ${retryResponse.status}`)
      }
      return retryResponse.json()
    } else {
      throw new Error('UNAUTHORIZED')
    }
  }

  if (!response.ok) {
    const errJson = await response.json().catch(() => ({}))
    throw new Error(errJson?.detail?.error?.message || `API error ${response.status}`)
  }

  return response.json()
}

export async function loginUser(credentials: {
  username: string
  password: string
}): Promise<{ access_token: string }> {
  const res = await fetchApi<{ access_token: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
  setAccessToken(res.access_token)
  return res
}

export async function logoutUser(): Promise<void> {
  try {
    await fetchApi('/auth/logout', { method: 'POST' })
  } finally {
    setAccessToken(null)
  }
}

export async function getMe(): Promise<AuthUser> {
  return fetchApi<AuthUser>('/auth/me')
}

export async function getDashboard(): Promise<DashboardPayload> {
  return fetchApi<DashboardPayload>('/api/v1/dashboard')
}

export function getStreamUrl(): string {
  const token = getAccessToken()
  const base = `${API_BASE_URL}/api/v1/stream`
  return token ? `${base}?token=${encodeURIComponent(token)}` : base
}
