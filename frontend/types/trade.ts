export interface TradeEntry {
  id: string
  timestamp: string
  agentId: string
  agentName: string
  agentType: "specialist" | "hybrid" | "master"
  direction: "BUY" | "SELL"
  size: number
  priceBefore: number
  priceAfter: number
  reasoning: string
  evidenceTitles: string[]
}
