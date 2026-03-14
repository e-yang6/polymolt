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

interface Props {
  priceHistory: number[]
}

function formatPct(v: number) {
  return `${Math.round(v * 100)}%`
}

export function ProbabilityChart({ priceHistory }: Props) {
  const data = priceHistory.map((p, i) => ({ trade: i + 1, probability: p }))

  const currentPrice = priceHistory[priceHistory.length - 1] ?? 0.5
  const lineColor =
    currentPrice >= 0.55 ? "#34d399" :   // emerald
    currentPrice <= 0.40 ? "#f87171" :   // rose
    "#fbbf24"                             // amber

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
          width={38}
        />
        <Tooltip
          contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #1e293b", borderRadius: 6 }}
          labelStyle={{ color: "#64748b", fontSize: 11 }}
          formatter={(value) => [formatPct(Number(value)), "Probability"]}
          labelFormatter={(label) => `Trade ${label}`}
          itemStyle={{ color: lineColor }}
        />
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
          activeDot={{ r: 4, fill: lineColor }}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
