import React, { useEffect, useState } from 'react'
import {
  getMe,
  loginUser,
  logoutUser,
  refreshAccessToken,
} from '../api/client'
import type { AuthUser } from '../types/dashboard'
import { AuthContext } from './authContextDef'

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let mounted = true

    async function initAuth() {
      try {
        const token = await refreshAccessToken()
        if (token && mounted) {
          const profile = await getMe()
          if (mounted) setUser(profile)
        }
      } catch {
        if (mounted) setUser(null)
      } finally {
        if (mounted) setIsLoading(false)
      }
    }

    initAuth()
    return () => {
      mounted = false
    }
  }, [])

  const login = async (credentials: { username: string; password: string }) => {
    await loginUser(credentials)
    const profile = await getMe()
    setUser(profile)
  }

  const logout = async () => {
    try {
      await logoutUser()
    } finally {
      setUser(null)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
