const base = (process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000").replace(/\/$/, "").trim()
const pathPrefix = (process.env.NEXT_PUBLIC_BACKEND_PATH_PREFIX ?? "").trim().replace(/^\/|\/$/g, "")
/** Backend base URL for API calls (market, ai, etc.). Add NEXT_PUBLIC_BACKEND_PATH_PREFIX=/api if the backend is served under /api. */
export const BACKEND_URL = pathPrefix ? `${base}/${pathPrefix}` : base
