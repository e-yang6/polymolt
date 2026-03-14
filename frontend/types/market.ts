export interface MarketState {
  regionId: string
  question: string
  currentPrice: number      // 0–1
  priceHistory: number[]
  roundNumber: number
  isRunning: boolean
  tradeCount: number
}

export interface Region {
  id: string
  name: string
  description: string
  profile: "sustainable" | "weak" | "contested"
  lmsr_b: number
}
