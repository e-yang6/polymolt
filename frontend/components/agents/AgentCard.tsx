"use client"

import { useState, useEffect, useRef } from "react"
import { Agent } from "@/types/agent"
import { AgentTypeBadge } from "@/components/shared/AgentTypeBadge"
import { CategoryBadge } from "@/components/shared/CategoryBadge"
import { ArrowUp, ArrowDown, Minus } from "lucide-react"

interface Props {
  agent: Agent
  onClick: () => void
}

function positionIcon(pos: number) {
  if (pos > 1) return <ArrowUp className="w-3 h-3 text-emerald-400" />
  if (pos < -1) return <ArrowDown className="w-3 h-3 text-rose-400" />
  return <Minus className="w-3 h-3 text-slate-500" />
}

export function AgentCard({ agent, onClick }: Props) {
  const beliefPct = Math.round(agent.currentBelief * 100)
  const [flash, setFlash] = useState(false)
  const prevBeliefRef = useRef(agent.currentBelief)

  useEffect(() => {
    if (Math.abs(agent.currentBelief - prevBeliefRef.current) > 0.001) {
      prevBeliefRef.current = agent.currentBelief
      setFlash(true)
      const t = setTimeout(() => setFlash(false), 600)
      return () => clearTimeout(t)
    }
  }, [agent.currentBelief])

  const beliefColor =
    beliefPct >= 55 ? "text-emerald-400" :
    beliefPct <= 40 ? "text-rose-400" :
    "text-amber-400"

  const lastTrade = agent.tradeHistory?.[0]
  const lastDelta = lastTrade
    ? (lastTrade.priceAfter - lastTrade.priceBefore) * 100
    : null

  return (
    <button
      onClick={onClick}
      className={`flex flex-col gap-2.5 p-3.5 bg-slate-900 rounded-xl border border-slate-800 hover:border-slate-700 hover:bg-slate-800/60 transition-all text-left cursor-pointer w-full ${flash ? "animate-flash-update" : ""}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-col gap-1 min-w-0">
          <span className="text-sm font-semibold text-slate-200 leading-tight truncate">
            {agent.name}
          </span>
          <AgentTypeBadge type={agent.agentType} />
        </div>
        <div className="flex flex-col items-end gap-1 flex-shrink-0">
          <span className={`text-lg font-bold tabular-nums ${beliefColor}`}>
            {beliefPct}%
          </span>
          {lastTrade && lastDelta !== null ? (
            <div className={`flex items-center gap-0.5 text-xs font-medium ${lastTrade.direction === "BUY" ? "text-emerald-400" : "text-rose-400"}`}>
              {lastTrade.direction === "BUY"
                ? <ArrowUp className="w-3 h-3" />
                : <ArrowDown className="w-3 h-3" />
              }
              <span>{lastDelta >= 0 ? "+" : ""}{lastDelta.toFixed(1)}pp</span>
            </div>
          ) : (
            <div className="flex items-center gap-0.5 text-xs text-slate-500">
              {positionIcon(agent.currentPosition)}
              <span>{agent.currentPosition.toFixed(1)}</span>
            </div>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-1">
        {agent.categories.map((cat) => (
          <CategoryBadge key={cat} category={cat} size="sm" />
        ))}
      </div>

      {agent.lastReasoning && (
        <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">
          {agent.lastReasoning}
        </p>
      )}
    </button>
  )
}
