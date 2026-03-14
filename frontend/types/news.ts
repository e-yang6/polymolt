export interface RegionNewsArticle {
  title: string
  link: string
  published: string
  summary: string
}

export interface RegionNewsResponse {
  region_id: string
  region_name: string
  query_used: string
  articles: RegionNewsArticle[]
  error?: string
}
