"use client"

import { useState } from "react"
import { useMarket } from "@/lib/useMarket"
import { Header } from "@/components/header/Header"
import { MarketPanel } from "@/components/market/MarketPanel"
import { BehaviorStudyView } from "@/components/market/BehaviorStudyView"
import { TradeFeed } from "@/components/trades/TradeFeed"
import { AgentGrid } from "@/components/agents/AgentGrid"
import { AgentDrawer } from "@/components/agents/AgentDrawer"
import { Region } from "@/types/market"
import { BarChart2, Zap, TrendingUp } from "lucide-react"

export default function HomePage() {
  const { market, agents, trades, regions, selectedRegion, connectionStatus, selectRegion, resetMarket, shockMarket } = useMarket("scandinavia")
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null)
  const [showStudyView, setShowStudyView] = useState(false)

  const selectedAgent = agents.find((a) => a.id === selectedAgentId) ?? null
  const currentRegion = (regions.find((r) => r.id === selectedRegion) ?? null) as Region | null

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      <Header
        regions={regions as Region[]}
        selectedRegion={selectedRegion}
        connectionStatus={connectionStatus}
        onSelectRegion={selectRegion}
        onReset={resetMarket}
      />

      <main className="flex-1 flex flex-col gap-4 p-4 lg:p-5 max-w-[1600px] mx-auto w-full">
        {/* Top row: market panel + trade feed */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-4" style={{ minHeight: 420 }}>
          <MarketPanel market={market} region={currentRegion} trades={trades} />
          <TradeFeed
            trades={trades}
            onAgentClick={(id) => setSelectedAgentId(id)}
          />
        </div>

        {/* Demo controls row */}
        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={() => setShowStudyView((v) => !v)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors ${
              showStudyView
                ? "bg-indigo-500/20 border-indigo-500/40 text-indigo-300"
                : "bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-300"
            }`}
          >
            <BarChart2 className="w-3.5 h-3.5" />
            {showStudyView ? "Hide" : "Show"} Belief Distribution
          </button>
          {showStudyView && market && (
            <span className="text-xs text-slate-600">
              All agents ranked by current belief estimate vs. market price
            </span>
          )}

          {/* Shock event demo buttons */}
          {market?.isRunning && (
            <div className="flex items-center gap-2 ml-auto">
              <span className="text-xs text-slate-600 hidden sm:block">Demo events:</span>
              <button
                onClick={() => shockMarket("negative")}
                title="Inject a crisis event — agents will respond within 2–3 rounds"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium bg-rose-500/10 border-rose-500/30 text-rose-400 hover:bg-rose-500/20 hover:border-rose-500/50 transition-colors"
              >
                <Zap className="w-3.5 h-3.5" />
                Shock
              </button>
              <button
                onClick={() => shockMarket("positive")}
                title="Inject a recovery event — agents will respond within 2–3 rounds"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20 hover:border-emerald-500/50 transition-colors"
              >
                <TrendingUp className="w-3.5 h-3.5" />
                Recover
              </button>
            </div>
          )}
        </div>

        {/* Behavior Study View (F4.6) */}
        {showStudyView && market && agents.length > 0 && (
          <BehaviorStudyView
            agents={agents}
            marketPrice={market.currentPrice}
            onAgentClick={(id) => setSelectedAgentId(id)}
          />
        )}

        {/* Bottom row: agent grid */}
        <AgentGrid
          agents={agents}
          onAgentClick={(id) => setSelectedAgentId(id)}
        />
      </main>

      {/* Agent detail drawer */}
      {selectedAgentId && (
        <>
          <div
            className="fixed inset-0 z-40 bg-black/50"
            onClick={() => setSelectedAgentId(null)}
          />
          <AgentDrawer
            agent={selectedAgent}
            marketPrice={market?.currentPrice}
            onClose={() => setSelectedAgentId(null)}
          />
        </>
      )}
    </div>
  )
}
