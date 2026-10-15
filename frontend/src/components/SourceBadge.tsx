import React from 'react'
import type { CardStatus, SourceInfo } from '../types/dashboard'
import './SourceBadge.css'

interface SourceBadgeProps {
  source?: SourceInfo
  asOf?: string | null
  status?: CardStatus
  notes?: string[]
}

export const SourceBadge: React.FC<SourceBadgeProps> = ({
  source,
  asOf,
  status,
  notes,
}) => {
  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return '—'
    try {
      const d = new Date(dateStr)
      if (isNaN(d.getTime())) return dateStr
      return d.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    } catch {
      return dateStr
    }
  }

  const notesText = notes && notes.length > 0 ? notes.join(' · ') : null

  return (
    <footer className="source-badge-footer">
      <div className="source-info-left">
        {source ? (
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="source-link"
            title={`View official data source: ${source.name}`}
          >
            Source: <span className="source-name">{source.name}</span>
          </a>
        ) : (
          <span className="source-unknown">Source: Official Public Release</span>
        )}

        {source && !source.is_nse && (
          <span className="non-nse-tag" title="Official public macroeconomic source (non-NSE)">
            Non-NSE
          </span>
        )}

        {status === 'stale' && (
          <span className="stale-pill" title="Upstream refresh delayed; retaining last valid snapshot">
            Stale
          </span>
        )}
      </div>

      <div className="source-info-right">
        {notesText && (
          <span className="source-note" title={notesText}>
            {notesText}
          </span>
        )}
        <span className="as-of-text">
          As of: <strong>{formatDate(asOf)}</strong>
        </span>
      </div>
    </footer>
  )
}
