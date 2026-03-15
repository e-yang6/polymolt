export interface SelectedFeature {
  name: string
  type: string
  coordinates: [number, number]
  layerId: string
}

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export interface HistoryItem {
  id: string
  question: string
  answer: string
  createdAt: string
}

export interface BetLocation {
  questionId: number
  questionText: string
  location: string
  coordinates: [number, number]
  createdAt: string
  yesCount: number
  noCount: number
}
