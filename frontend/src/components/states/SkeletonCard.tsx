import React from 'react'
import './States.css'

export const SkeletonCard: React.FC = () => {
  return (
    <div className="card-skeleton" aria-busy="true" aria-label="Loading card data">
      <div className="skeleton-header">
        <div className="skeleton-bar skeleton-title" />
      </div>
      <div className="skeleton-kpis">
        <div className="skeleton-kpi-tile">
          <div className="skeleton-circle" />
          <div className="skeleton-kpi-lines">
            <div className="skeleton-bar skeleton-label" />
            <div className="skeleton-bar skeleton-value" />
          </div>
        </div>
        <div className="skeleton-kpi-tile">
          <div className="skeleton-circle" />
          <div className="skeleton-kpi-lines">
            <div className="skeleton-bar skeleton-label" />
            <div className="skeleton-bar skeleton-value" />
          </div>
        </div>
      </div>
      <div className="skeleton-chart" />
      <div className="skeleton-footer">
        <div className="skeleton-bar skeleton-foot" />
      </div>
    </div>
  )
}
