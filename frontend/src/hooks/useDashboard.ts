import { useQuery } from '@tanstack/react-query'
import { getDashboard } from '../api/client'
import type { DashboardPayload } from '../types/dashboard'
import type { StreamStatus } from './useSSE'

export function useDashboard(enabled: boolean, streamStatus: StreamStatus) {
  return useQuery<DashboardPayload>({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
    enabled,
    staleTime: 10000,
    // Poll every 30s only if SSE is not LIVE (offline or delayed fallback)
    refetchInterval: streamStatus === 'LIVE' ? false : 30000,
    refetchOnWindowFocus: true,
  })
}
