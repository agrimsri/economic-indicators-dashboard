import React from 'react'
import type { StreamStatus } from '../hooks/useSSE'
import type { TickerItem } from '../types/dashboard'
import './Ticker.css'

interface TickerProps {
  items: TickerItem[]
  marketStatus: string
  streamStatus: StreamStatus
}

export const Ticker: React.FC<TickerProps> = ({
  items,
  marketStatus,
  streamStatus,
}) => {
  const formatPrice = (val: number | null) => {
    if (val === null || val === undefined) return '—'
    return val.toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  }

  const formatDelta = (val: number | null, pct: number | null) => {
    if (val === null || pct === null) return '—'
    const sign = pct > 0 ? '+' : ''
    return `${sign}${pct.toFixed(2)}%`
  }

  const renderBadge = () => {
    if (streamStatus === 'LIVE') {
      const isMarketOpen = marketStatus.toLowerCase() === 'open'
      return (
        <div className="ticker-badge live-badge" title={`NSE Feed: Live (${marketStatus})`}>
          <span className="live-dot" />
          <span className="live-text">LIVE</span>
          {!isMarketOpen && <span className="market-note">· Closed</span>}
        </div>
      )
    }

    if (streamStatus === 'DELAYED') {
      return (
        <div className="ticker-badge delayed-badge" title="Feed delayed: Polling active">
          <span className="delayed-dot" />
          <span className="delayed-text">DELAYED</span>
        </div>
      )
    }

    return (
      <div className="ticker-badge offline-badge" title="Feed offline">
        <span className="offline-dot" />
        <span className="offline-text">OFFLINE</span>
      </div>
    )
  }

  // Double items for seamless infinite marquee loop
  const displayItems = items.length > 0 ? [...items, ...items] : []

  return (
    <div
      className="ticker-container"
      role="region"
      aria-label="Live Market Indices Ticker"
    >
      <div className="ticker-badge-wrapper">{renderBadge()}</div>

      <div className="ticker-marquee-wrapper" tabIndex={0} aria-live="off">
        {items.length === 0 ? (
          <div className="ticker-empty">Market ticker data synchronizing...</div>
        ) : (
          <div className="ticker-track">
            {displayItems.map((item, idx) => {
              const isPositive = (item.percent_change ?? 0) >= 0
              const colorClass =
                item.percent_change === null
                  ? 'neutral'
                  : isPositive
                  ? 'positive'
                  : 'negative'

              return (
                <div
                  key={`${item.symbol}-${idx}`}
                  className="ticker-item"
                  title={`${item.symbol}: ${item.last ?? '—'} (${item.percent_change ?? '—'}%)`}
                >
                  <span className="ticker-symbol">
                    {item.symbol}
                    {!item.is_nse && <span className="bse-tag">BSE</span>}
                  </span>
                  <span className="ticker-price">{formatPrice(item.last)}</span>
                  <span className={`ticker-delta ${colorClass}`}>
                    {item.percent_change !== null && (isPositive ? '▲' : '▼')}{' '}
                    {formatDelta(item.variation, item.percent_change)}
                  </span>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
