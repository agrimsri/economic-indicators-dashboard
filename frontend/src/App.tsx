import React, { useState } from 'react'
import flagIndia from './assets/flag-india.png'
import flagUs from './assets/flag-us.png'
import iconGlobe from './assets/icon-globe.png'
import artExports from './assets/art-exports.png'
import artImports from './assets/art-imports.png'
import artGstCoins from './assets/art-gst-coins.png'
import artGstCalendar from './assets/art-gst-calendar.png'
import artInflationBasket from './assets/art-inflation-basket.png'
import artRbiTarget from './assets/art-rbi-target.png'
import artExpRev from './assets/art-expenditure-rev.png'
import artExpCap from './assets/art-expenditure-cap.png'
import { useAuth } from './auth/useAuth'
import { Card } from './components/Card'
import { DebtChart } from './components/charts/DebtChart'
import { ExpenditureChart } from './components/charts/ExpenditureChart'
import { GdpChart } from './components/charts/GdpChart'
import { GstChart } from './components/charts/GstChart'
import { InflationChart } from './components/charts/InflationChart'
import { TradeChart } from './components/charts/TradeChart'
import { Header } from './components/Header'
import { KpiTile } from './components/KpiTile'
import { LoginModal } from './components/LoginModal'
import { ErrorState } from './components/states/StateComponents'
import { SkeletonCard } from './components/states/SkeletonCard'
import { Ticker } from './components/Ticker'
import { useDashboard } from './hooks/useDashboard'
import { useSSE } from './hooks/useSSE'
import './App.css'

export const App: React.FC = () => {
  const { isAuthenticated, isLoading: isAuthLoading } = useAuth()
  const [isLoginOpen, setIsLoginOpen] = useState(false)

  const { streamStatus } = useSSE(isAuthenticated)
  const {
    data: dashboardData,
    isLoading: isDataLoading,
    isError,
    error,
    refetch,
  } = useDashboard(isAuthenticated, streamStatus)

  const cards = dashboardData?.cards || {}
  const tickerItems = dashboardData?.ticker?.items || []
  const marketStatus = dashboardData?.ticker?.market_status || 'Closed'

  const showSkeleton = isAuthLoading || (isAuthenticated && isDataLoading)

  return (
    <div className="dashboard-app">
      <Header onOpenLogin={() => setIsLoginOpen(true)} />

      <main className="dashboard-viewport">
        {/* Ticker Row */}
        <Ticker
          items={tickerItems}
          marketStatus={marketStatus}
          streamStatus={streamStatus}
        />

        {/* Unauthenticated Reviewer Banner */}
        {!isAuthenticated && !isAuthLoading && (
          <div
            style={{
              background: 'rgba(15, 202, 240, 0.08)',
              border: '1px solid rgba(15, 202, 240, 0.25)',
              borderRadius: '8px',
              padding: '12px 20px',
              margin: '0 0 20px 0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              color: '#ffffff',
              fontSize: '13px',
            }}
          >
            <span>
              🔒 Authentication required to connect to the live FastAPI backend & SSE stream.
            </span>
            <button
              onClick={() => setIsLoginOpen(true)}
              style={{
                background: 'var(--text-cyan)',
                border: 'none',
                color: '#07122a',
                padding: '6px 14px',
                borderRadius: '4px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Sign In with Evaluation Credentials
            </button>
          </div>
        )}

        {/* Global Error Banner if initial fetch fails */}
        {isAuthenticated && isError && (
          <div style={{ marginBottom: '20px' }}>
            <ErrorState
              message={error?.message || 'Failed to fetch dashboard snapshot'}
              onRetry={() => refetch()}
            />
          </div>
        )}

        {/* 2 Columns x 3 Rows Responsive Grid */}
        <div className="dashboard-grid">
          {/* Card 1: GDP */}
          <div className="grid-card-cell">
            {showSkeleton ? (
              <SkeletonCard />
            ) : (
              <Card
                title="GDP (INDIA VS WORLD)"
                qualifier="YoY%"
                snapshot={cards['gdp']}
                kpis={
                  <>
                    <KpiTile
                      data={cards['gdp']?.kpis[0]}
                      icon={flagIndia}
                      altIcon="India Flag"
                    />
                    <KpiTile
                      data={cards['gdp']?.kpis[1]}
                      icon={iconGlobe}
                      altIcon="World Globe"
                    />
                  </>
                }
              >
                <GdpChart series={cards['gdp']?.series || []} />
              </Card>
            )}
          </div>

          {/* Card 2: Debt to GDP */}
          <div className="grid-card-cell">
            {showSkeleton ? (
              <SkeletonCard />
            ) : (
              <Card
                title="DEBT TO GDP (INDIA VS US)"
                qualifier="YoY%"
                snapshot={cards['debt']}
                kpis={
                  <>
                    <KpiTile
                      data={cards['debt']?.kpis[0]}
                      icon={flagIndia}
                      altIcon="India Flag"
                    />
                    <KpiTile
                      data={cards['debt']?.kpis[1]}
                      icon={flagUs}
                      altIcon="US Flag"
                    />
                  </>
                }
              >
                <DebtChart series={cards['debt']?.series || []} />
              </Card>
            )}
          </div>

          {/* Card 3: Trade */}
          <div className="grid-card-cell">
            {showSkeleton ? (
              <SkeletonCard />
            ) : (
              <Card
                title="EXPORTS & IMPORTS (INDIA)"
                qualifier="US$ B"
                snapshot={cards['trade']}
                kpis={
                  <>
                    <KpiTile
                      data={cards['trade']?.kpis[0]}
                      icon={artExports}
                      altIcon="Exports Art"
                    />
                    <KpiTile
                      data={cards['trade']?.kpis[1]}
                      icon={artImports}
                      altIcon="Imports Art"
                    />
                  </>
                }
              >
                <TradeChart series={cards['trade']?.series || []} />
              </Card>
            )}
          </div>

          {/* Card 4: GST */}
          <div className="grid-card-cell">
            {showSkeleton ? (
              <SkeletonCard />
            ) : (
              <Card
                title="GST REVENUE COLLECTION (INDIA)"
                qualifier="₹ LAKH CR"
                snapshot={cards['gst']}
                kpis={
                  <>
                    <KpiTile
                      data={cards['gst']?.kpis[0]}
                      icon={artGstCoins}
                      altIcon="GST Coins"
                    />
                    <KpiTile
                      data={cards['gst']?.kpis[1]}
                      icon={artGstCalendar}
                      altIcon="GST Calendar"
                    />
                  </>
                }
              >
                <GstChart series={cards['gst']?.series || []} />
              </Card>
            )}
          </div>

          {/* Card 5: Inflation */}
          <div className="grid-card-cell">
            {showSkeleton ? (
              <SkeletonCard />
            ) : (
              <Card
                title="INFLATION RATE (CPI)"
                qualifier="YoY%"
                snapshot={cards['inflation']}
                kpis={
                  <>
                    <KpiTile
                      data={cards['inflation']?.kpis[0]}
                      icon={artInflationBasket}
                      altIcon="Inflation Basket"
                    />
                    <KpiTile
                      data={cards['inflation']?.kpis[1]}
                      icon={artRbiTarget}
                      altIcon="RBI Target"
                    />
                  </>
                }
              >
                <InflationChart series={cards['inflation']?.series || []} />
              </Card>
            )}
          </div>

          {/* Card 6: Fiscal */}
          <div className="grid-card-cell">
            {showSkeleton ? (
              <SkeletonCard />
            ) : (
              <Card
                title="GOVERNMENT EXPENDITURE"
                qualifier="₹ LAKH CR"
                snapshot={cards['fiscal']}
                kpis={
                  <>
                    <KpiTile
                      data={cards['fiscal']?.kpis[0]}
                      icon={artExpRev}
                      altIcon="Revenue Expenditure"
                    />
                    <KpiTile
                      data={cards['fiscal']?.kpis[1]}
                      icon={artExpCap}
                      altIcon="Capital Expenditure"
                    />
                  </>
                }
              >
                <ExpenditureChart series={cards['fiscal']?.series || []} />
              </Card>
            )}
          </div>
        </div>
      </main>

      <LoginModal
        isOpen={isLoginOpen || (!isAuthenticated && !isAuthLoading)}
        onClose={() => setIsLoginOpen(false)}
      />
    </div>
  )
}

export default App
