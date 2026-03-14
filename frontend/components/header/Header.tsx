"use client"

import { Region } from "@/types/market"
import { ConnectionStatus } from "@/lib/useMarket"
import { RegionSelector } from "./RegionSelector"
import { RotateCcw, Wifi, WifiOff } from "lucide-react"

interface Props {
  regions: Region[]
  selectedRegion: string
  connectionStatus: ConnectionStatus
  onSelectRegion: (id: string) => void
  onReset: () => void
}

const STATUS_STYLES: Record<ConnectionStatus, string> = {
  connected: "text-emerald-400",
  connecting: "text-amber-400",
  disconnected: "text-slate-500",
  error: "text-rose-400",
}

export function Header({ regions, selectedRegion, connectionStatus, onSelectRegion, onReset }: Props) {
  const isConnected = connectionStatus === "connected"

  return (
    <header className="sticky top-0 z-50 flex items-center justify-between px-6 py-3 bg-slate-950/90 backdrop-blur border-b border-slate-800">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center">
            <span className="text-emerald-400 text-xs font-bold">P</span>
          </div>
          <span className="font-bold text-slate-100 text-lg tracking-tight">Polymolt</span>
        </div>
        <span className="text-slate-600 text-sm hidden sm:block">|</span>
        <span className="text-slate-500 text-xs hidden sm:block">Sustainability Prediction Market</span>
      </div>

      <div className="flex items-center gap-3">
        <RegionSelector
          regions={regions}
          selectedRegion={selectedRegion}
          onSelect={onSelectRegion}
        />

        <button
          onClick={onReset}
          title="Reset market"
          className="flex items-center gap-1.5 px-3 py-2 text-xs text-slate-400 bg-slate-800 border border-slate-700 rounded-lg hover:text-slate-200 hover:border-slate-600 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset
        </button>

        <div className={`flex items-center gap-1.5 text-xs font-medium ${STATUS_STYLES[connectionStatus]}`}>
          {isConnected ? (
            <Wifi className="w-3.5 h-3.5" />
          ) : (
            <WifiOff className="w-3.5 h-3.5" />
          )}
          <span className="hidden sm:block capitalize">{connectionStatus}</span>
        </div>
      </div>
    </header>
  )
}
