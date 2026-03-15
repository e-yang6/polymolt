"use client"

import { useState } from "react"
import { ChevronDown, ChevronRight, MapPin } from "lucide-react"
import type { BetLocation } from "@/types/map"

interface BetLocationListProps {
  bets: BetLocation[]
  loading: boolean
  onBetClick: (bet: BetLocation) => void
  activeBetId: number | null
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" })
}

export function BetLocationList({ bets, loading, onBetClick, activeBetId }: BetLocationListProps) {
  const [collapsed, setCollapsed] = useState(false)

  const totalBets = bets.length
  const yesTotal = bets.reduce((s, b) => s + b.yesCount, 0)
  const noTotal = bets.reduce((s, b) => s + b.noCount, 0)

  return (
    <div className="rounded-xl bg-white/95 backdrop-blur shadow-lg border border-neutral-200 overflow-hidden max-h-[calc(100vh-180px)] flex flex-col">
      <button
        type="button"
        onClick={() => setCollapsed((c) => !c)}
        className="flex items-center justify-between w-full px-4 py-3 text-left hover:bg-neutral-50 transition-colors"
      >
        <div className="flex items-center gap-2 min-w-0">
          <MapPin className="w-4 h-4 text-blue-500 flex-shrink-0" />
          <span className="text-sm font-semibold text-neutral-900 truncate">
            Bets on Map
          </span>
          {totalBets > 0 && (
            <span className="flex-shrink-0 text-xs text-neutral-500 bg-neutral-100 rounded-full px-2 py-0.5">
              {totalBets}
            </span>
          )}
        </div>
        {collapsed ? (
          <ChevronRight className="w-4 h-4 text-neutral-400 flex-shrink-0" />
        ) : (
          <ChevronDown className="w-4 h-4 text-neutral-400 flex-shrink-0" />
        )}
      </button>

      {!collapsed && (
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="px-4 py-6 text-center">
              <div className="inline-block w-5 h-5 border-2 border-neutral-300 border-t-neutral-600 rounded-full animate-spin" />
              <p className="mt-2 text-xs text-neutral-500">Loading bets…</p>
            </div>
          ) : bets.length === 0 ? (
            <p className="px-4 py-4 text-xs text-neutral-500 text-center">
              No bets with locations yet.
            </p>
          ) : (
            <>
              <div className="px-4 py-2 border-t border-neutral-100 flex gap-3 text-xs text-neutral-500">
                <span className="text-emerald-600 font-medium">{yesTotal} YES</span>
                <span className="text-red-500 font-medium">{noTotal} NO</span>
              </div>
              <ul className="border-t border-neutral-100">
                {bets.map((bet) => {
                  const isActive = activeBetId === bet.questionId
                  const total = bet.yesCount + bet.noCount
                  const yesPct = total > 0 ? Math.round((bet.yesCount / total) * 100) : 50
                  return (
                    <li key={bet.questionId}>
                      <button
                        type="button"
                        onClick={() => onBetClick(bet)}
                        className={`w-full text-left px-4 py-3 border-b border-neutral-100 last:border-b-0 transition-colors hover:bg-blue-50/60 ${
                          isActive ? "bg-blue-50 ring-1 ring-inset ring-blue-200" : ""
                        }`}
                      >
                        <p className="text-sm font-medium text-neutral-900 line-clamp-2 leading-snug">
                          {bet.questionText}
                        </p>
                        <div className="mt-1.5 flex items-center gap-2 text-xs text-neutral-500">
                          <span className="truncate max-w-[140px]" title={bet.location}>
                            {bet.location}
                          </span>
                          <span className="text-neutral-300">·</span>
                          <span>{formatDate(bet.createdAt)}</span>
                        </div>
                        {total > 0 && (
                          <div className="mt-2 flex items-center gap-2">
                            <div className="flex-1 h-1.5 rounded-full bg-neutral-100 overflow-hidden">
                              <div
                                className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-emerald-500"
                                style={{ width: `${yesPct}%` }}
                              />
                            </div>
                            <span className="text-[11px] font-medium text-neutral-600 tabular-nums w-8 text-right">
                              {yesPct}%
                            </span>
                          </div>
                        )}
                      </button>
                    </li>
                  )
                })}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  )
}
