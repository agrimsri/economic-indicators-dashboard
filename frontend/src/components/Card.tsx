import React from 'react'
import cornerFoldImg from '../assets/corner-fold.png'
import type { CardSnapshot, CardStatus } from '../types/dashboard'
import { SourceBadge } from './SourceBadge'
import { StaleBanner, UnavailableState } from './states/StateComponents'
import './Card.css'

interface CardProps {
  title: string
  qualifier?: string
  snapshot?: CardSnapshot
  kpis?: React.ReactNode
  children?: React.ReactNode
  isLoading?: boolean
}

export const Card: React.FC<CardProps> = ({
  title,
  qualifier,
  snapshot,
  kpis,
  children,
}) => {
  const status: CardStatus = snapshot?.status || 'fresh'
  const isUnavailable = status === 'unavailable'
  const isStale = status === 'stale'

  return (
    <article className="dashboard-card" aria-label={`${title} ${qualifier || ''}`}>
      {/* Distinctive Figma Folded Corner Accent */}
      <img
        src={cornerFoldImg}
        alt=""
        className="card-corner-fold"
        aria-hidden="true"
      />

      {/* Header Strip */}
      <header className="card-header">
        <h2 className="card-title">
          {title}{' '}
          {qualifier && <span className="card-qualifier">({qualifier})</span>}
        </h2>
      </header>

      {/* Stale Alert Banner if upstream delayed */}
      {isStale && <StaleBanner message={snapshot?.message} />}

      {/* KPI Tiles Strip */}
      {kpis && <div className="card-kpis">{kpis}</div>}

      {/* Chart or State Body */}
      <div className="card-body">
        {isUnavailable ? (
          <UnavailableState message={snapshot?.message} />
        ) : (
          children
        )}
      </div>

      {/* Source & Timestamp Footer */}
      <SourceBadge
        source={snapshot?.source}
        asOf={snapshot?.as_of}
        status={status}
        notes={snapshot?.notes}
      />
    </article>
  )
}
