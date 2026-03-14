"use client"

import { MarketState, Region } from "@/types/market"
import { ProbabilityDisplay } from "./ProbabilityDisplay"
import { ProbabilityChart } from "./ProbabilityChart"

interface Props {
  market: MarketState | null
  region: Region | null
}

export function MarketPanel({ market, region }: Props) {
  return (
    <div className="flex flex-col gap-4 p-5 bg-slate-900 rounded-xl border border-slate-800 h-full">
      {market ? (
        <>
          <ProbabilityDisplay
            price={market.currentPrice}
            priceHistory={market.priceHistory}
            question={market.question}
          />

          {region && (
            <p className="text-xs text-slate-500 leading-relaxed border-t border-slate-800 pt-3">
              {region.description}
            </p>
          )}

          <div className="flex-1 min-h-[220px]">
            <ProbabilityChart priceHistory={market.priceHistory} />
          </div>

          <div className="flex items-center gap-4 text-xs text-slate-600 border-t border-slate-800 pt-3">
            <span>Round {market.roundNumber}</span>
            <span>•</span>
            <span>{market.tradeCount} trades</span>
            <span>•</span>
            <span className={market.isRunning ? "text-emerald-500" : "text-slate-500"}>
              {market.isRunning ? "● Live" : "○ Paused"}
            </span>
          </div>
        </>
      ) : (
        <div className="flex flex-col gap-3">
          <div className="h-16 w-40 rounded bg-slate-800 animate-pulse" />
          <div className="flex-1 min-h-[220px] rounded bg-slate-800 animate-pulse" />
        </div>
      )}
    </div>
  )
}
