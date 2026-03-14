"use client"

import { Agent } from "@/types/agent"
import { AgentCard } from "./AgentCard"
import { Bot } from "lucide-react"

interface Props {
  agents: Agent[]
  onAgentClick: (agentId: string) => void
}

export function AgentGrid({ agents, onAgentClick }: Props) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <Bot className="w-4 h-4 text-slate-500" />
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Agent Roster
        </span>
        <span className="text-xs text-slate-600">{agents.length} agents active</span>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {agents.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            onClick={() => onAgentClick(agent.id)}
          />
        ))}
        {agents.length === 0 &&
          Array.from({ length: 9 }).map((_, i) => (
            <div key={i} className="h-28 rounded-xl bg-slate-900 border border-slate-800 animate-pulse" />
          ))
        }
      </div>
    </div>
  )
}
