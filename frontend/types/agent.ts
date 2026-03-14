import { TradeEntry } from "./trade"
import { EvidenceItem } from "./evidence"

export interface Agent {
  id: string
  name: string
  agentType: "specialist" | "hybrid" | "master"
  categories: string[]
  bettingPower: number
  confidence: number
  effectiveConfidence: number
  riskTolerance: number
  maxPosition: number
  stubbornness: number
  herdSensitivity: number
  updateFrequency: number
  contrarian: boolean
  currentBelief: number
  currentPosition: number
  lastReasoning: string
  evidenceUsed: EvidenceItem[]
  tradeHistory: TradeEntry[]
  beliefHistory: number[]
}
