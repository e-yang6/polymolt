export interface QuestionSummary {
  id: number
  question_text: string
  location: string
  created_at: string
  yes_count: number
  no_count: number
}

export interface StakeholderResponse {
  id: number
  question_id: number
  stakeholder_id: string
  stakeholder_role: string
  ai_agent_id: string
  answer: string
  confidence: number | null
  reasoning: string | null
  created_at: string
}

export interface QuestionDetail {
  question: QuestionSummary
  responses: StakeholderResponse[]
}

