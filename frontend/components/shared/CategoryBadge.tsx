import { CATEGORY_COLORS, CATEGORY_LABELS } from "@/lib/constants"

interface Props {
  category: string
  size?: "sm" | "md"
}

export function CategoryBadge({ category, size = "sm" }: Props) {
  const color = CATEGORY_COLORS[category] ?? "text-slate-400 bg-slate-400/10 border-slate-400/20"
  const label = CATEGORY_LABELS[category] ?? category
  const px = size === "sm" ? "px-1.5 py-0.5 text-xs" : "px-2 py-1 text-sm"

  return (
    <span className={`inline-flex items-center rounded border font-medium ${px} ${color}`}>
      {label}
    </span>
  )
}
