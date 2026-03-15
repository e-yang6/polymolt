"use client"

import { useMemo, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowRight, X } from "lucide-react"
import type { SelectedFeature, BetLocation } from "@/types/map"

interface LocationSidePanelProps {
  feature: SelectedFeature
  onClose: () => void
  isMobile: boolean
  betLocations?: BetLocation[]
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric" })
}

export function LocationSidePanel({ feature, onClose, isMobile, betLocations = [] }: LocationSidePanelProps) {
  const router = useRouter()
  const [input, setInput] = useState("")
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const locationBets = useMemo(() => {
    const name = feature.name.toLowerCase().trim()
    return betLocations.filter((b) => b.location.toLowerCase().trim() === name)
  }, [feature.name, betLocations])

  const sendMessage = () => {
    const q = input.trim()
    if (!q) return
    const params = new URLSearchParams({
      question: q,
      location: feature.name,
    })
    router.push(`/dashboard?${params.toString()}`)
    onClose()
  }

  const goToBet = (bet: BetLocation) => {
    const hasVotes = bet.yesCount + bet.noCount > 0
    if (hasVotes) {
      router.push(`/dashboard?question_id=${bet.questionId}`)
    } else {
      const params = new URLSearchParams({
        question: bet.questionText,
        location: bet.location,
      })
      router.push(`/dashboard?${params.toString()}`)
    }
    onClose()
  }

  const [lng, lat] = feature.coordinates
  const coordText = `${lat.toFixed(5)}, ${lng.toFixed(5)}`

  const panelWidth = isMobile ? "100%" : "380px"

  return (
    <div
      className={`fixed top-0 z-40 flex flex-col bg-white shadow-2xl border-l border-neutral-200 overflow-hidden ${isMobile ? "left-0 right-0 bottom-0 max-h-[85vh] rounded-t-2xl" : "right-0 h-full"}`}
      style={!isMobile ? { width: panelWidth } : undefined}
      role="dialog"
      aria-modal="true"
      aria-labelledby="location-panel-title"
    >
      <div className="flex-shrink-0 flex items-start justify-between gap-3 p-5 border-b border-neutral-100">
          <div className="min-w-0">
            <h2 id="location-panel-title" className="font-semibold text-neutral-900 text-lg truncate">
              {feature.name}
            </h2>
            <span className="inline-block mt-1.5 px-2 py-0.5 rounded-md text-xs bg-neutral-100 text-neutral-600">
              {feature.type}
            </span>
            <p className="mt-1 text-xs text-neutral-400">{coordText}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex-shrink-0 p-2 rounded-lg hover:bg-neutral-100 text-neutral-500 hover:text-neutral-700 transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          <div>
            <label htmlFor="location-question-input" className="block text-sm font-medium text-neutral-700 mb-2">
              Ask a question about this place
            </label>
            <div className="flex gap-2">
              <input
                ref={inputRef}
                id="location-question-input"
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault()
                    sendMessage()
                  }
                }}
                placeholder="e.g. Is this place accessible?"
                className="flex-1 rounded-xl border border-neutral-200 bg-neutral-50 text-neutral-900 placeholder-neutral-400 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent"
              />
              <button
                type="button"
                onClick={sendMessage}
                disabled={!input.trim()}
                className="px-4 py-2.5 rounded-xl bg-neutral-900 text-white text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-neutral-800 transition-colors"
              >
                Ask
              </button>
            </div>
            {error && (
              <p className="mt-2 text-sm text-red-600 flex items-center gap-2">
                {error}
                <button type="button" onClick={() => setError(null)} className="underline">
                  Dismiss
                </button>
              </p>
            )}
            <p className="mt-2 text-xs text-neutral-500">
              After you ask, you&apos;ll be taken to the market view to see predictions and the graph.
            </p>
          </div>

          <div>
            <h3 className="text-sm font-medium text-neutral-700 mb-3">
              Past bets{locationBets.length > 0 && (
                <span className="ml-1.5 text-neutral-400 font-normal">({locationBets.length})</span>
              )}
            </h3>
            {locationBets.length === 0 ? (
              <p className="text-sm text-neutral-500">No bets for this location yet.</p>
            ) : (
              <ul className="space-y-2.5">
                {locationBets.map((bet) => {
                  const total = bet.yesCount + bet.noCount
                  const yesPct = total > 0 ? Math.round((bet.yesCount / total) * 100) : null
                  return (
                    <li key={bet.questionId}>
                      <button
                        type="button"
                        onClick={() => goToBet(bet)}
                        className="w-full text-left rounded-xl border border-neutral-200 bg-neutral-50/80 p-3 hover:border-neutral-400 hover:shadow-sm transition-all group"
                      >
                        <p className="text-sm font-medium text-neutral-900 line-clamp-2 leading-snug">
                          {bet.questionText}
                        </p>
                        <div className="mt-2 flex items-center gap-2 text-xs text-neutral-500">
                          <span>{formatDate(bet.createdAt)}</span>
                          {yesPct != null && (
                            <>
                              <span className="text-neutral-300">·</span>
                              <span className="text-emerald-600 font-medium">Yes {yesPct}%</span>
                              <span className="text-neutral-300">·</span>
                              <span>{total} votes</span>
                            </>
                          )}
                          {yesPct == null && <span>No votes yet</span>}
                        </div>
                        <div className="mt-2 flex items-center gap-1 text-xs font-medium text-neutral-900 group-hover:text-blue-600 transition-colors">
                          View bet
                          <ArrowRight className="w-3 h-3" />
                        </div>
                      </button>
                    </li>
                  )
                })}
              </ul>
            )}
          </div>
        </div>
    </div>
  )
}
