"use client"

import { TrendingUp, TrendingDown, Minus } from "lucide-react"

interface Props {
  price: number          // 0–1
  priceHistory: number[]
  question: string
}

function getTrend(history: number[]): "up" | "down" | "flat" {
  if (history.length < 3) return "flat"
  const recent = history.slice(-5)
  const delta = recent[recent.length - 1] - recent[0]
  if (delta > 0.005) return "up"
  if (delta < -0.005) return "down"
  return "flat"
}

export function ProbabilityDisplay({ price, priceHistory, question }: Props) {
  const pct = Math.round(price * 100)
  const trend = getTrend(priceHistory)

  const colorClass =
    pct >= 55 ? "text-emerald-400" :
    pct <= 40 ? "text-rose-400" :
    "text-amber-400"

  const TrendIcon = trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Minus
  const trendColor = trend === "up" ? "text-emerald-400" : trend === "down" ? "text-rose-400" : "text-slate-500"

  return (
    <div className="flex flex-col items-start gap-1">
      <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">{question}</p>
      <div className="flex items-end gap-3">
        <span className={`text-6xl font-black tabular-nums leading-none ${colorClass}`}>
          {pct}<span className="text-3xl">%</span>
        </span>
        <div className={`flex items-center gap-1 mb-1 ${trendColor}`}>
          <TrendIcon className="w-5 h-5" />
          <span className="text-sm font-medium capitalize">{trend}</span>
        </div>
      </div>
      <p className="text-xs text-slate-600">probability this region is sustainable</p>
    </div>
  )
}
