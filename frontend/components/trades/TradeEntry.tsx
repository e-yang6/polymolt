import { TradeEntry as TradeEntryType } from "@/types/trade"
import { AGENT_TYPE_COLORS } from "@/lib/constants"
import { ArrowUp, ArrowDown } from "lucide-react"

interface Props {
  trade: TradeEntryType
  onAgentClick?: (agentId: string) => void
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString("en-US", {
      hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false
    })
  } catch {
    return iso
  }
}

function fmtPct(n: number): string {
  return `${(n * 100).toFixed(1)}%`
}

export function TradeEntryRow({ trade, onAgentClick }: Props) {
  const isBuy = trade.direction === "BUY"
  const delta = trade.priceAfter - trade.priceBefore
  const deltaSign = delta >= 0 ? "+" : ""

  return (
    <div className={`animate-slide-in-down flex flex-col gap-1 px-3 py-2.5 border-b border-slate-800/60 border-l-2 hover:bg-slate-800/30 transition-colors ${isBuy ? "border-l-emerald-500/50" : "border-l-rose-500/50"}`}>
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className={`flex-shrink-0 flex items-center gap-0.5 text-xs font-semibold ${isBuy ? "text-emerald-400" : "text-rose-400"}`}>
            {isBuy ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
            {trade.direction}
          </div>
          <button
            onClick={() => onAgentClick?.(trade.agentId)}
            className={`text-xs font-medium truncate hover:underline ${AGENT_TYPE_COLORS[trade.agentType]?.split(" ")[0] ?? "text-slate-300"}`}
          >
            {trade.agentName}
          </button>
          <span className="text-xs text-slate-600 flex-shrink-0">{trade.size.toFixed(1)}u</span>
        </div>
        <div className="flex items-center gap-2 text-xs flex-shrink-0">
          <span className="text-slate-500">{fmtPct(trade.priceBefore)}</span>
          <span className="text-slate-600">→</span>
          <span className={isBuy ? "text-emerald-400" : "text-rose-400"}>
            {fmtPct(trade.priceAfter)}
          </span>
          <span className={`font-mono text-xs ${delta >= 0 ? "text-emerald-500" : "text-rose-500"}`}>
            ({deltaSign}{(delta * 100).toFixed(1)}pp)
          </span>
        </div>
      </div>
      <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">{trade.reasoning}</p>
      <span className="text-xs text-slate-700">{formatTime(trade.timestamp)}</span>
    </div>
  )
}
