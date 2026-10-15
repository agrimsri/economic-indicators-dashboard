import React from 'react'
import './States.css'

export const EmptyState: React.FC<{ message?: string }> = ({
  message = 'No observation records found for this period.',
}) => {
  return (
    <div className="card-state card-empty-state">
      <div className="state-icon">📊</div>
      <p className="state-message">{message}</p>
    </div>
  )
}

export const ErrorState: React.FC<{ message?: string; onRetry?: () => void }> = ({
  message = 'Failed to load indicator data.',
  onRetry,
}) => {
  return (
    <div className="card-state card-error-state">
      <div className="state-icon">⚠️</div>
      <p className="state-message">{message}</p>
      {onRetry && (
        <button className="state-retry-btn" onClick={onRetry}>
          Retry Fetch
        </button>
      )}
    </div>
  )
}

export const StaleBanner: React.FC<{ message?: string | null }> = ({ message }) => {
  return (
    <div className="stale-banner" role="alert">
      <span className="stale-icon">⏳</span>
      <span className="stale-text">
        {message || 'Upstream data source delayed · Preserving last known valid snapshot'}
      </span>
    </div>
  )
}

export const UnavailableState: React.FC<{ message?: string | null }> = ({
  message,
}) => {
  return (
    <div className="card-state card-unavailable-state">
      <div className="state-icon">🔒</div>
      <p className="state-title">Indicator Unavailable</p>
      <p className="state-message">
        {message || 'Upstream observation unavailable. Zero fabricated numbers are rendered.'}
      </p>
    </div>
  )
}
