export interface EvidenceItem {
  id: string
  category: string
  title: string
  summary: string
  sentiment: "positive" | "negative" | "mixed"
  strength: number  // 0–1
}
