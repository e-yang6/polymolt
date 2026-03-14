"use client"

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts"
import { TradeEntry } from "@/types/trade"

interface DataPoint {
  trade: number
  probability: number
  agentName?: string
  direction?: "BUY" | "SELL"
}

interface Props {
  priceHistory: number[]
  trades?: TradeEntry[]
}

function formatPct(v: number) {
  return `${(v * 100).toFixed(1)}%`
}

interface TooltipProps {
  active?: boolean
  payload?: Array<{ value: number; payload: DataPoint }>
}

function ChartTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  const isBuy = d.direction === "BUY"
  return (
    <div style={{
      backgroundColor: "#0f172a",
      border: "1px solid #1e293b",
      borderRadius: 8,
      padding: "8px 12px",
      minWidth: 120,
    }}>
      <div style={{ color: "#64748b", fontSize: 11, marginBottom: 4 }}>Trade #{d.trade}</div>
      {d.agentName && (
        <div style={{ color: isBuy ? "#34d399" : "#f87171", fontSize: 11, marginBottom: 2 }}>
          {d.direction} · {d.agentName}
        </div>
      )}
      <div style={{ color: "#f8fafc", fontSize: 14, fontWeight: 700 }}>
        {formatPct(d.probability)}
      </div>
    </div>
  )
}

export function ProbabilityChart({ priceHistory, trades }: Props) {
  // Build data from trades (chronological) if available, else from priceHistory
  const data: DataPoint[] = trades && trades.length > 0
    ? [...trades].reverse().map((t, i) => ({
        trade: i + 1,
        probability: t.priceAfter,
        agentName: t.agentName,
        direction: t.direction,
      }))
    : priceHistory.map((p, i) => ({ trade: i + 1, probability: p }))

  const currentPrice = data[data.length - 1]?.probability ?? 0.5
  const lineColor =
    currentPrice >= 0.55 ? "#34d399" :
    currentPrice <= 0.40 ? "#f87171" :
    "#fbbf24"

  if (data.length < 2) {
    return (
      <div className="flex items-center justify-center h-full text-slate-600 text-sm">
        Waiting for trades...
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis
          dataKey="trade"
          tick={{ fill: "#475569", fontSize: 11 }}
          axisLine={{ stroke: "#1e293b" }}
          tickLine={false}
          label={{ value: "Trade #", position: "insideBottomRight", fill: "#475569", fontSize: 11, offset: -5 }}
        />
        <YAxis
          domain={[0, 1]}
          tickFormatter={formatPct}
          tick={{ fill: "#475569", fontSize: 11 }}
          axisLine={{ stroke: "#1e293b" }}
          tickLine={false}
          width={44}
        />
        <Tooltip content={<ChartTooltip />} />
        <ReferenceLine
          y={0.5}
          stroke="#334155"
          strokeDasharray="4 4"
          label={{ value: "50%", fill: "#475569", fontSize: 10, position: "left" }}
        />
        <Line
          type="monotone"
          dataKey="probability"
          stroke={lineColor}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 5, fill: lineColor, stroke: "#0f172a", strokeWidth: 2 }}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
