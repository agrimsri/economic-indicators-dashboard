import { useEffect, useRef, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { getAccessToken, getStreamUrl } from '../api/client'
import type { CardSnapshot, DashboardPayload, TickerPayload } from '../types/dashboard'

export type StreamStatus = 'LIVE' | 'DELAYED' | 'OFFLINE'

export function useSSE(enabled: boolean) {
  const queryClient = useQueryClient()
  const [streamStatus, setStreamStatus] = useState<StreamStatus>('OFFLINE')
  const retryTimeoutRef = useRef<number | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)
  const lastPingRef = useRef<number>(0)

  useEffect(() => {
    if (!enabled) {
      return
    }

    let retryCount = 0
    let isSubscribed = true

    function connect() {
      if (!isSubscribed) return

      const token = getAccessToken()
      if (!token) {
        setStreamStatus('DELAYED')
        return
      }

      const streamUrl = getStreamUrl()
      const es = new EventSource(streamUrl)
      eventSourceRef.current = es

      es.onopen = () => {
        if (!isSubscribed) return
        retryCount = 0
        setStreamStatus('LIVE')
        lastPingRef.current = Date.now()
      }

      es.addEventListener('ping', () => {
        lastPingRef.current = Date.now()
        setStreamStatus('LIVE')
      })

      es.addEventListener('ticker', (event: MessageEvent) => {
        try {
          const data: TickerPayload = JSON.parse(event.data)
          queryClient.setQueryData<DashboardPayload>(['dashboard'], (old) => {
            if (!old) return old
            return {
              ...old,
              ticker: data,
            }
          })
        } catch (err) {
          console.error('Failed to parse ticker SSE event:', err)
        }
      })

      es.addEventListener('card-update', (event: MessageEvent) => {
        try {
          const data: CardSnapshot = JSON.parse(event.data)
          queryClient.setQueryData<DashboardPayload>(['dashboard'], (old) => {
            if (!old) return old
            return {
              ...old,
              cards: {
                ...old.cards,
                [data.card]: data,
              },
            }
          })
        } catch (err) {
          console.error('Failed to parse card-update SSE event:', err)
        }
      })

      es.onerror = () => {
        es.close()
        eventSourceRef.current = null
        if (!isSubscribed) return

        setStreamStatus('DELAYED')
        const backoff = Math.min(1000 * Math.pow(2, retryCount), 15000)
        retryCount++
        retryTimeoutRef.current = window.setTimeout(connect, backoff)
      }
    }

    connect()

    // Liveness checker for ping
    const pingCheckInterval = window.setInterval(() => {
      if (lastPingRef.current > 0 && Date.now() - lastPingRef.current > 45000) {
        setStreamStatus((prev) => (prev === 'LIVE' ? 'DELAYED' : prev))
      }
    }, 15000)

    return () => {
      isSubscribed = false
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current)
      }
      clearInterval(pingCheckInterval)
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
    }
  }, [enabled, queryClient])

  return { streamStatus: enabled ? streamStatus : 'OFFLINE' }
}
