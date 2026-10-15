import React from 'react'
import './DeltaChip.css'

interface DeltaChipProps {
  delta: number | null | undefined
  unit?: string | null
  basis?: string | null
}

export const DeltaChip: React.FC<DeltaChipProps> = ({ delta, unit, basis }) => {
  if (delta === null || delta === undefined) {
    return (
      <span className="delta-chip neutral" title={basis || 'No comparison delta'}>
        <span className="delta-arrow">—</span>
      </span>
    )
  }

  const isPositive = delta > 0
  const isZero = delta === 0
  const sign = isPositive ? '+' : ''
  const displayUnit = unit ? ` ${unit}` : '%'
  const formattedVal = `${sign}${delta.toFixed(2)}${displayUnit}`

  const variantClass = isZero ? 'neutral' : isPositive ? 'positive' : 'negative'
  const arrow = isZero ? '—' : isPositive ? '▲' : '▼'
  const tooltip = basis ? `${basis}: ${formattedVal}` : formattedVal

  return (
    <span className={`delta-chip ${variantClass}`} title={tooltip}>
      <span className="delta-arrow">{arrow}</span>
      <span className="delta-val">{formattedVal}</span>
    </span>
  )
}
