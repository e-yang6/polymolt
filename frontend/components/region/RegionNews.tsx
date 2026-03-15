"use client"

import { useEffect, useState } from "react"
import { Region } from "@/types/market"
import { RegionNewsResponse } from "@/types/news"
import { BACKEND_URL as API_BASE } from "@/lib/config"

interface Props {
  region: Region | null
}

function formatDate(published: string): string {
  if (!published) return ""
  try {
    const d = new Date(published)
    return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })
  } catch {
    return published
  }
}

export function RegionNews({ region }: Props) {
  const [data, setData] = useState<RegionNewsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!region?.id) {
      setData(null)
      setError(null)
      return
    }
    setLoading(true)
    setError(null)
    fetch(`${API_BASE}/regions/${region.id}/news?max_items=8`)
      .then((r) => {
        if (!r.ok) throw new Error("Failed to load news")
        return r.json()
      })
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load news"))
      .finally(() => setLoading(false))
  }, [region?.id])

  if (!region) return null

  return (
    <section className="rounded-lg border border-neutral-200 bg-neutral-50/50 overflow-hidden">
      <div className="px-4 py-3 border-b border-neutral-200 bg-white">
        <h2 className="text-sm font-semibold text-neutral-800">
          News for this area
        </h2>
        <p className="text-xs text-neutral-500 mt-0.5">
          {region.name}
        </p>
      </div>
      <div className="p-4 min-h-[120px]">
        {loading && (
          <p className="text-sm text-neutral-500">Loading news…</p>
        )}
        {error && (
          <p className="text-sm text-amber-700">{error}</p>
        )}
        {data?.error && !data.articles?.length && (
          <p className="text-sm text-amber-700">News temporarily unavailable.</p>
        )}
        {data?.articles && data.articles.length > 0 && (
          <ul className="space-y-3">
            {data.articles.map((article, i) => (
              <li key={i} className="text-sm">
                <a
                  href={article.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium text-neutral-800 hover:text-neutral-600 underline underline-offset-2"
                >
                  {article.title}
                </a>
                {article.published && (
                  <span className="ml-2 text-neutral-400 text-xs">
                    {formatDate(article.published)}
                  </span>
                )}
                {article.summary && (
                  <p className="mt-1 text-neutral-600 line-clamp-2">{article.summary}</p>
                )}
              </li>
            ))}
          </ul>
        )}
        {!loading && !error && data && !data.error && (!data.articles || data.articles.length === 0) && (
          <p className="text-sm text-neutral-500">No recent articles found for this region.</p>
        )}
      </div>
    </section>
  )
}
