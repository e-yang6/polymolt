"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { MarketState, Region } from "@/types/market"
import { Agent } from "@/types/agent"
import { TradeEntry } from "@/types/trade"

const WS_BASE = "ws://localhost:8000"
const API_BASE = "http://localhost:8000"
const MAX_TRADES = 150

export type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error"

interface UseMarketReturn {
  market: MarketState | null
  agents: Agent[]
  trades: TradeEntry[]
  regions: Region[]
  selectedRegion: string
  connectionStatus: ConnectionStatus
  selectRegion: (regionId: string) => void
  resetMarket: () => void
}

export function useMarket(defaultRegion = "scandinavia"): UseMarketReturn {
  const [market, setMarket] = useState<MarketState | null>(null)
  const [agents, setAgents] = useState<Agent[]>([])
  const [trades, setTrades] = useState<TradeEntry[]>([])
  const [regions, setRegions] = useState<Region[]>([])
  const [selectedRegion, setSelectedRegion] = useState(defaultRegion)
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>("connecting")

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const currentRegionRef = useRef(defaultRegion)

  // Fetch region list once
  useEffect(() => {
    fetch(`${API_BASE}/regions`)
      .then((r) => r.json())
      .then((data) => setRegions(data.regions ?? []))
      .catch(console.error)
  }, [])

  const connect = useCallback((regionId: string) => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setConnectionStatus("connecting")
    const ws = new WebSocket(`${WS_BASE}/ws/${regionId}`)
    wsRef.current = ws

    ws.onopen = () => {
      setConnectionStatus("connected")
    }

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        handleMessage(msg)
      } catch (e) {
        console.error("WS parse error", e)
      }
    }

    ws.onerror = () => {
      setConnectionStatus("error")
    }

    ws.onclose = () => {
      setConnectionStatus("disconnected")
      // Auto-reconnect after 3s
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      reconnectTimer.current = setTimeout(() => {
        connect(currentRegionRef.current)
      }, 3000)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const handleMessage = useCallback((msg: { type: string; data: unknown }) => {
    switch (msg.type) {
      case "market_reset": {
        const d = msg.data as { agents?: Agent[]; recentTrades?: TradeEntry[] } & MarketState
        setMarket({
          regionId: d.regionId,
          question: d.question,
          currentPrice: d.currentPrice,
          priceHistory: d.priceHistory ?? [],
          roundNumber: d.roundNumber,
          isRunning: d.isRunning,
          tradeCount: d.tradeCount ?? 0,
        })
        if (d.agents) setAgents(d.agents)
        if (d.recentTrades) setTrades(d.recentTrades)
        else setTrades([])
        break
      }

      case "trade": {
        const d = msg.data as { trade: TradeEntry; agent: Agent; market: MarketState }
        setTrades((prev) => {
          const next = [d.trade, ...prev]
          return next.slice(0, MAX_TRADES)
        })
        setMarket(d.market)
        setAgents((prev) =>
          prev.map((a) => (a.id === d.agent.id ? d.agent : a))
        )
        break
      }

      case "agent_update": {
        const agent = msg.data as Agent
        setAgents((prev) =>
          prev.map((a) => (a.id === agent.id ? agent : a))
        )
        break
      }

      case "ping":
        wsRef.current?.send(JSON.stringify({ type: "pong" }))
        break

      default:
        break
    }
  }, [])

  // Initial connection
  useEffect(() => {
    connect(defaultRegion)
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      if (wsRef.current) wsRef.current.close()
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const selectRegion = useCallback((regionId: string) => {
    currentRegionRef.current = regionId
    setSelectedRegion(regionId)
    setTrades([])
    setMarket(null)

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "change_region", regionId }))
    } else {
      connect(regionId)
    }
  }, [connect])

  const resetMarket = useCallback(() => {
    setTrades([])
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "reset" }))
    }
  }, [])

  return {
    market,
    agents,
    trades,
    regions,
    selectedRegion,
    connectionStatus,
    selectRegion,
    resetMarket,
  }
}
