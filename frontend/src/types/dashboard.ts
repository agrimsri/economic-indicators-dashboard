export type CardStatus = 'fresh' | 'stale' | 'unavailable'

export interface SourceInfo {
  id: string
  name: string
  url: string
  is_nse: boolean
}

export interface KpiTileData {
  key: string
  label: string
  value: number | null
  unit: string
  delta: number | null
  delta_unit?: string | null
  delta_basis?: string | null
}

export interface SeriesPoint {
  x: string
  y: number | null
  estimate?: boolean
}

export interface SeriesData {
  key: string
  label: string
  points: SeriesPoint[]
}

export interface CardSnapshot {
  card: string
  status: CardStatus
  as_of: string | null
  fetched_at: string
  source: SourceInfo
  kpis: KpiTileData[]
  series: SeriesData[]
  notes: string[]
  message?: string | null
}

export interface TickerItem {
  symbol: string
  last: number | null
  variation: number | null
  percent_change: number | null
  is_nse: boolean
  status: CardStatus
}

export interface TickerPayload {
  items: TickerItem[]
  market_status: string
  as_of: string | null
}

export interface DashboardPayload {
  ticker: TickerPayload
  cards: Record<string, CardSnapshot>
}

export interface AuthUser {
  username: string
  role: string
}
