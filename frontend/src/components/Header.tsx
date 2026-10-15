import React from 'react'
import headerTexture from '../assets/header-candlesticks.png'
import { useAuth } from '../auth/useAuth'
import './Header.css'

interface HeaderProps {
  onOpenLogin?: () => void
}

export const Header: React.FC<HeaderProps> = ({ onOpenLogin }) => {
  const { user, isAuthenticated, logout } = useAuth()

  return (
    <header className="dashboard-header" role="banner">
      <div
        className="header-texture"
        style={{ backgroundImage: `url(${headerTexture})` }}
        aria-hidden="true"
      />
      <div className="header-content">
        <h1 className="header-title">ECONOMIC INDICATOR</h1>
        <div className="header-actions">
          {isAuthenticated && user ? (
            <div className="user-badge-container">
              <span className="user-badge">
                <span className="user-dot" />
                <span className="user-name">{user.username}</span>
              </span>
              <button
                className="auth-btn logout-btn"
                onClick={() => logout()}
                title="Sign out of evaluation session"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <button
              className="auth-btn login-btn"
              onClick={onOpenLogin}
              title="Sign in with evaluation credentials"
            >
              Sign In
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
