import { AGENT_TYPE_COLORS, AGENT_TYPE_LABELS } from "@/lib/constants"

interface Props {
  type: string
}

export function AgentTypeBadge({ type }: Props) {
  const color = AGENT_TYPE_COLORS[type] ?? "text-slate-400 bg-slate-400/10 border-slate-400/20"
  const label = AGENT_TYPE_LABELS[type] ?? type

  return (
    <span className={`inline-flex items-center rounded border px-1.5 py-0.5 text-xs font-medium ${color}`}>
      {label}
    </span>
  )
}
