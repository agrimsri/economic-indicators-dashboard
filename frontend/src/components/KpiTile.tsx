import React from 'react'
import type { KpiTileData } from '../types/dashboard'
import { DeltaChip } from './DeltaChip'
import './KpiTile.css'

interface KpiTileProps {
  data?: KpiTileData
  icon?: string
  altIcon?: string
}

export const KpiTile: React.FC<KpiTileProps> = ({ data, icon, altIcon }) => {
  const formatValue = (val: number | null | undefined, unit: string = '') => {
    if (val === null || val === undefined) return '—'
    const formattedNum = val.toLocaleString('en-IN', {
      maximumFractionDigits: 2,
    })

    // If unit starts with ₹ or $, display as prefix
    if (unit.startsWith('₹')) {
      const restUnit = unit.replace('₹', '').trim()
      return `₹${formattedNum}${restUnit ? ` ${restUnit}` : ''}`
    }
    if (unit.startsWith('$')) {
      const restUnit = unit.replace('$', '').trim()
      return `$${formattedNum}${restUnit ? ` ${restUnit}` : ''}`
    }

    return `${formattedNum}${unit ? ` ${unit}` : ''}`
  }

  return (
    <div className="kpi-tile">
      {icon && (
        <div className="kpi-icon-container">
          <img src={icon} alt={altIcon || data?.label || 'KPI icon'} className="kpi-icon" />
        </div>
      )}
      <div className="kpi-details">
        <div className="kpi-header-row">
          <span className="kpi-label">{data?.label || '—'}</span>
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value">
            {formatValue(data?.value, data?.unit)}
          </span>
          <DeltaChip
            delta={data?.delta}
            unit={data?.delta_unit}
            basis={data?.delta_basis}
          />
        </div>
      </div>
    </div>
  )
}
