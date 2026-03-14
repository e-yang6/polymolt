"use client"

import { Agent } from "@/types/agent"
import { EvidenceItem } from "@/types/evidence"
import { CategoryBadge } from "@/components/shared/CategoryBadge"
import { AgentTypeBadge } from "@/components/shared/AgentTypeBadge"
import { X, ArrowUp, ArrowDown } from "lucide-react"
import { CATEGORY_LABELS } from "@/lib/constants"

interface Props {
  agent: Agent | null
  onClose: () => void
}

function TraitBar({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100)
  const barColor =
    pct >= 70 ? "bg-emerald-500" :
    pct >= 40 ? "bg-amber-500" :
    "bg-slate-600"

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-slate-500 w-28 flex-shrink-0">{label}</span>
      <div className="flex-1 bg-slate-800 rounded-full h-1.5">
        <div
          className={`h-1.5 rounded-full transition-all ${barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs text-slate-500 w-8 text-right tabular-nums">{pct}%</span>
    </div>
  )
}

function EvidenceCard({ item }: { item: EvidenceItem }) {
  const sentimentStyle =
    item.sentiment === "positive" ? "text-emerald-400 bg-emerald-400/5 border-emerald-400/20" :
    item.sentiment === "negative" ? "text-rose-400 bg-rose-400/5 border-rose-400/20" :
    "text-amber-400 bg-amber-400/5 border-amber-400/20"

  return (
    <div className={`rounded-lg border p-2.5 ${sentimentStyle}`}>
      <div className="flex items-start justify-between gap-2 mb-1">
        <span className="text-xs font-medium leading-snug">{item.title}</span>
        <span className="text-xs opacity-60 flex-shrink-0">{Math.round(item.strength * 100)}%</span>
      </div>
      <p className="text-xs opacity-70 leading-relaxed">{item.summary}</p>
      <div className="flex items-center gap-1.5 mt-1.5">
        <CategoryBadge category={item.category} size="sm" />
        <span className="text-xs opacity-50 capitalize">{item.sentiment}</span>
      </div>
    </div>
  )
}

export function AgentDrawer({ agent, onClose }: Props) {
  if (!agent) return null

  const beliefPct = Math.round(agent.currentBelief * 100)
  const beliefColor =
    beliefPct >= 55 ? "text-emerald-400" :
    beliefPct <= 40 ? "text-rose-400" :
    "text-amber-400"

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-[420px] bg-slate-950 border-l border-slate-800 overflow-y-auto shadow-2xl">
      {/* Header */}
      <div className="sticky top-0 bg-slate-950/95 backdrop-blur px-5 py-4 border-b border-slate-800 flex items-start justify-between gap-3">
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center gap-2">
            <span className="text-base font-bold text-slate-100">{agent.name}</span>
            <AgentTypeBadge type={agent.agentType} />
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span>Power: <span className="text-slate-300">{agent.bettingPower}x</span></span>
            <span>•</span>
            <span>Position: <span className={agent.currentPosition >= 0 ? "text-emerald-400" : "text-rose-400"}>
              {agent.currentPosition >= 0 ? "+" : ""}{agent.currentPosition.toFixed(1)}
            </span></span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-slate-500 hover:text-slate-300 transition-colors mt-0.5"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="px-5 py-4 space-y-5">
        {/* Belief vs Market */}
        <section>
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Current Belief</h3>
          <div className="flex items-center gap-3">
            <div className="flex flex-col items-center px-4 py-2.5 bg-slate-900 rounded-lg border border-slate-800">
              <span className="text-xs text-slate-500 mb-0.5">My Estimate</span>
              <span className={`text-2xl font-black ${beliefColor}`}>{beliefPct}%</span>
            </div>
            <div className="text-slate-600 text-lg">vs</div>
            <div className="flex flex-col items-center px-4 py-2.5 bg-slate-900 rounded-lg border border-slate-800">
              <span className="text-xs text-slate-500 mb-0.5">Market</span>
              <span className="text-2xl font-black text-slate-300">—</span>
            </div>
          </div>
        </section>

        {/* Categories */}
        <section>
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Knowledge Access</h3>
          <div className="flex flex-wrap gap-1.5">
            {agent.categories.map((cat) => (
              <CategoryBadge key={cat} category={cat} size="md" />
            ))}
          </div>
        </section>

        {/* Behavior Traits */}
        <section>
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Behavior Traits</h3>
          <div className="space-y-2">
            <TraitBar label="Confidence" value={agent.confidence} />
            <TraitBar label="Risk Tolerance" value={agent.riskTolerance} />
            <TraitBar label="Stubbornness" value={agent.stubbornness} />
            <TraitBar label="Herd Sensitivity" value={agent.herdSensitivity} />
            <TraitBar label="Update Frequency" value={agent.updateFrequency} />
          </div>
          {agent.contrarian && (
            <div className="mt-2 text-xs text-rose-400 bg-rose-400/10 border border-rose-400/20 rounded px-2 py-1">
              ↺ Contrarian — trades against consensus
            </div>
          )}
        </section>

        {/* Latest Reasoning */}
        {agent.lastReasoning && (
          <section>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Latest Reasoning</h3>
            <p className="text-sm text-slate-300 leading-relaxed bg-slate-900 rounded-lg border border-slate-800 p-3">
              {agent.lastReasoning}
            </p>
          </section>
        )}

        {/* Evidence Used */}
        {agent.evidenceUsed && agent.evidenceUsed.length > 0 && (
          <section>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Evidence Used ({agent.evidenceUsed.length} items)
            </h3>
            <div className="space-y-2">
              {agent.evidenceUsed.slice(0, 5).map((item) => (
                <EvidenceCard key={item.id} item={item} />
              ))}
            </div>
          </section>
        )}

        {/* Trade History */}
        {agent.tradeHistory && agent.tradeHistory.length > 0 && (
          <section>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Recent Trades</h3>
            <div className="space-y-1.5">
              {agent.tradeHistory.slice(0, 5).map((trade, i) => (
                <div key={i} className="flex items-center justify-between text-xs px-2.5 py-2 bg-slate-900 rounded-lg border border-slate-800">
                  <div className="flex items-center gap-2">
                    {trade.direction === "BUY"
                      ? <ArrowUp className="w-3 h-3 text-emerald-400" />
                      : <ArrowDown className="w-3 h-3 text-rose-400" />
                    }
                    <span className={trade.direction === "BUY" ? "text-emerald-400" : "text-rose-400"}>
                      {trade.direction}
                    </span>
                    <span className="text-slate-500">{trade.size?.toFixed(1)}u</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-500">
                    <span>{((trade.priceBefore ?? 0) * 100).toFixed(1)}%</span>
                    <span>→</span>
                    <span className={trade.direction === "BUY" ? "text-emerald-400" : "text-rose-400"}>
                      {((trade.priceAfter ?? 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  )
}
