import { createContext } from 'react'
import type { AuthUser } from '../types/dashboard'

export interface AuthContextType {
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: { username: string; password: string }) => Promise<void>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)
