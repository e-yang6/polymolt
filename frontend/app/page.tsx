"use client"

import { useState } from "react"
import { useMarket } from "@/lib/useMarket"
import { Header } from "@/components/header/Header"
import { MarketPanel } from "@/components/market/MarketPanel"
import { TradeFeed } from "@/components/trades/TradeFeed"
import { AgentGrid } from "@/components/agents/AgentGrid"
import { AgentDrawer } from "@/components/agents/AgentDrawer"
import { Region } from "@/types/market"

export default function HomePage() {
  const { market, agents, trades, regions, selectedRegion, connectionStatus, selectRegion, resetMarket } = useMarket("scandinavia")
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null)

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
          <MarketPanel market={market} region={currentRegion} />
          <TradeFeed
            trades={trades}
            onAgentClick={(id) => setSelectedAgentId(id)}
          />
        </div>

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
            onClose={() => setSelectedAgentId(null)}
          />
        </>
      )}
    </div>
  )
}
