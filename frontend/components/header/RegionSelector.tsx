"use client"

import { Region } from "@/types/market"
import { ChevronDown } from "lucide-react"

const PROFILE_DOT: Record<string, string> = {
  sustainable: "bg-emerald-400",
  weak: "bg-rose-400",
  contested: "bg-amber-400",
}

interface Props {
  regions: Region[]
  selectedRegion: string
  onSelect: (regionId: string) => void
}

export function RegionSelector({ regions, selectedRegion, onSelect }: Props) {
  const selected = regions.find((r) => r.id === selectedRegion)

  return (
    <div className="relative">
      <select
        value={selectedRegion}
        onChange={(e) => onSelect(e.target.value)}
        className="appearance-none bg-slate-800 border border-slate-700 rounded-lg pl-3 pr-8 py-2 text-sm text-slate-200 cursor-pointer hover:border-slate-600 focus:outline-none focus:border-slate-500 transition-colors"
      >
        {regions.map((region) => (
          <option key={region.id} value={region.id}>
            {region.name}
          </option>
        ))}
        {regions.length === 0 && (
          <option value={selectedRegion}>Loading regions...</option>
        )}
      </select>
      <div className="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none flex items-center gap-1">
        {selected && (
          <span className={`w-1.5 h-1.5 rounded-full ${PROFILE_DOT[selected.profile] ?? "bg-slate-500"}`} />
        )}
        <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
      </div>
    </div>
  )
}
