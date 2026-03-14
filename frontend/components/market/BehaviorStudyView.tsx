"use client"

import { Agent } from "@/types/agent"
import { BarChart2 } from "lucide-react"

interface Props {
  agents: Agent[]
  marketPrice: number
  onAgentClick?: (agentId: string) => void
}

function beliefHex(v: number): string {
  if (v >= 0.55) return "#34d399"
  if (v <= 0.40) return "#f87171"
  return "#fbbf24"
}

function beliefTextClass(v: number): string {
  if (v >= 0.55) return "text-emerald-400"
  if (v <= 0.40) return "text-rose-400"
  return "text-amber-400"
}

export function BehaviorStudyView({ agents, marketPrice, onAgentClick }: Props) {
  const sorted = [...agents].sort((a, b) => b.currentBelief - a.currentBelief)
  const marketPct = Math.round(marketPrice * 100)

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-800 p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <BarChart2 className="w-4 h-4 text-slate-500" />
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Agent Belief Distribution
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-amber-400">
          <span className="inline-block w-3 border-t border-dashed border-amber-400/70" />
          <span>Market {marketPct}%</span>
        </div>
      </div>

      <div className="space-y-1.5">
        {sorted.map((agent) => {
          const gap = agent.currentBelief - marketPrice
          const isAbove = gap > 0.02
          const isBelow = gap < -0.02

          return (
            <button
              key={agent.id}
              onClick={() => onAgentClick?.(agent.id)}
              className="flex items-center gap-2 w-full hover:bg-slate-800/50 rounded px-1 py-1 transition-colors group"
            >
              {/* Agent name */}
              <span className="text-xs text-slate-400 w-36 text-left truncate group-hover:text-slate-200 transition-colors flex-shrink-0">
                {agent.name}
              </span>

              {/* Bar */}
              <div className="flex-1 relative h-3.5 bg-slate-800 rounded overflow-visible">
                <div
                  className="h-full rounded transition-all duration-500"
                  style={{
                    width: `${agent.currentBelief * 100}%`,
                    backgroundColor: beliefHex(agent.currentBelief),
                    opacity: 0.75,
                  }}
                />
                {/* Market price tick on this bar */}
                <div
                  className="absolute top-1/2 -translate-y-1/2 w-px h-5 pointer-events-none z-10"
                  style={{
                    left: `${marketPrice * 100}%`,
                    backgroundColor: "rgba(251, 191, 36, 0.7)",
                  }}
                />
              </div>

              {/* Belief % */}
              <span className={`text-xs w-8 text-right tabular-nums font-semibold flex-shrink-0 ${beliefTextClass(agent.currentBelief)}`}>
                {Math.round(agent.currentBelief * 100)}%
              </span>

              {/* Position label */}
              <span className={`text-xs w-10 text-right flex-shrink-0 ${isAbove ? "text-emerald-500" : isBelow ? "text-rose-500" : "text-slate-600"}`}>
                {isAbove ? "▲BULL" : isBelow ? "▼BEAR" : "≈MKT"}
              </span>
            </button>
          )
        })}
      </div>

      <p className="text-xs text-slate-600 mt-3 text-center">
        Click an agent to inspect their reasoning and evidence
      </p>
    </div>
  )
}
