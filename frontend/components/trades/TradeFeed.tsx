"use client"

import { useEffect, useRef } from "react"
import { TradeEntry } from "@/types/trade"
import { TradeEntryRow } from "./TradeEntry"
import { Activity } from "lucide-react"

interface Props {
  trades: TradeEntry[]
  onAgentClick?: (agentId: string) => void
}

export function TradeFeed({ trades, onAgentClick }: Props) {
  const topRef = useRef<HTMLDivElement>(null)

  // Scroll to top when new trade arrives
  useEffect(() => {
    topRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [trades.length])

  return (
    <div className="flex flex-col bg-slate-900 rounded-xl border border-slate-800 h-full overflow-hidden">
      <div className="flex items-center gap-2 px-3 py-2.5 border-b border-slate-800">
        <Activity className="w-3.5 h-3.5 text-slate-500" />
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Live Trade Feed</span>
        <span className="ml-auto text-xs text-slate-600">{trades.length} trades</span>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div ref={topRef} />
        {trades.length === 0 ? (
          <div className="flex items-center justify-center h-24 text-slate-600 text-sm">
            Waiting for trades...
          </div>
        ) : (
          trades.map((trade) => (
            <TradeEntryRow
              key={trade.id}
              trade={trade}
              onAgentClick={onAgentClick}
            />
          ))
        )}
      </div>
    </div>
  )
}
