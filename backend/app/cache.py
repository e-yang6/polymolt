"""
Upstash Redis caching layer.

Provides cache get/set/invalidate for:
- Embedding vectors (deterministic, long TTL)
- RAG vector retrieval results (medium TTL, invalidated on ingest)
- DB read queries (short TTL, invalidated on writes)
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from app.config import UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN

logger = logging.getLogger(__name__)

_redis = None

# TTL constants (seconds)
TTL_EMBEDDING = 86_400      # 24h — embeddings are deterministic for same input
TTL_RAG_RETRIEVAL = 3_600   # 1h  — stale after new documents ingested
TTL_DB_READ = 300           # 5m  — stale after DB writes

# Namespace constants
NS_EMBEDDING = "embed"
NS_RAG = "rag"
NS_DB = "db"


def get_redis():
    """Lazy-init the Upstash Redis client (singleton)."""
    global _redis
    if _redis is None:
        if not UPSTASH_REDIS_REST_URL or not UPSTASH_REDIS_REST_TOKEN:
            raise RuntimeError(
                "Upstash Redis not configured. "
                "Set UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN."
            )
        from upstash_redis import Redis
        _redis = Redis(url=UPSTASH_REDIS_REST_URL, token=UPSTASH_REDIS_REST_TOKEN)
    return _redis


def _make_key(namespace: str, *parts: Any) -> str:
    """Deterministic cache key: namespace:sha256(json(parts))."""
    raw = json.dumps(parts, sort_keys=True, default=str)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:32]
    return f"{namespace}:{digest}"


def cache_get(namespace: str, *key_parts: Any) -> Any | None:
    """Fetch from cache.  Returns None on miss or any error."""
    try:
        r = get_redis()
        key = _make_key(namespace, *key_parts)
        val = r.get(key)
        if val is None:
            return None
        return json.loads(val) if isinstance(val, str) else val
    except Exception as e:
        logger.debug("cache_get(%s) error: %s", namespace, e)
        return None


def cache_set(namespace: str, *key_parts: Any, value: Any, ttl: int) -> None:
    """Write to cache with TTL (seconds).  Fails silently."""
    try:
        r = get_redis()
        key = _make_key(namespace, *key_parts)
        r.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception as e:
        logger.debug("cache_set(%s) error: %s", namespace, e)


def cache_delete(namespace: str, *key_parts: Any) -> None:
    """Delete a single cache entry.  Fails silently."""
    try:
        r = get_redis()
        key = _make_key(namespace, *key_parts)
        r.delete(key)
    except Exception as e:
        logger.debug("cache_delete(%s) error: %s", namespace, e)


def cache_invalidate_namespace(namespace: str) -> int:
    """Delete ALL keys under a namespace using SCAN.  Returns count deleted."""
    deleted = 0
    try:
        r = get_redis()
        cursor: int = 0
        while True:
            cursor, keys = r.scan(cursor, match=f"{namespace}:*", count=200)
            if keys:
                for key in keys:
                    r.delete(key)
                    deleted += 1
            if cursor == 0:
                break
    except Exception as e:
        logger.debug("cache_invalidate_namespace(%s) error: %s", namespace, e)
    return deleted


def cache_invalidate_rag(collection_name: str | None = None) -> int:
    """Invalidate RAG retrieval cache.

    If collection_name given, only invalidates keys for that collection
    (by scanning for the sub-prefix).  Otherwise clears the full NS_RAG namespace.
    """
    prefix = f"{NS_RAG}:{collection_name}" if collection_name else NS_RAG
    deleted = 0
    try:
        r = get_redis()
        cursor: int = 0
        while True:
            cursor, keys = r.scan(cursor, match=f"{prefix}*", count=200)
            if keys:
                for key in keys:
                    r.delete(key)
                    deleted += 1
            if cursor == 0:
                break
    except Exception as e:
        logger.debug("cache_invalidate_rag(%s) error: %s", collection_name, e)
    return deleted


def _rag_key(collection_name: str, *extra: Any) -> str:
    """Build a RAG cache key that starts with NS_RAG:collection_name: so
    collection-scoped invalidation works correctly."""
    raw = json.dumps(extra, sort_keys=True, default=str)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:32]
    return f"{NS_RAG}:{collection_name}:{digest}"


def rag_cache_get(collection_name: str, *extra: Any) -> Any | None:
    """RAG-specific cache get (keys are namespaced by collection)."""
    try:
        r = get_redis()
        key = _rag_key(collection_name, *extra)
        val = r.get(key)
        if val is None:
            return None
        return json.loads(val) if isinstance(val, str) else val
    except Exception as e:
        logger.debug("rag_cache_get(%s) error: %s", collection_name, e)
        return None


def rag_cache_set(collection_name: str, *extra: Any, value: Any, ttl: int) -> None:
    """RAG-specific cache set (keys are namespaced by collection)."""
    try:
        r = get_redis()
        key = _rag_key(collection_name, *extra)
        r.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception as e:
        logger.debug("rag_cache_set(%s) error: %s", collection_name, e)


def redis_health() -> dict[str, Any]:
    """Quick health check: PING + key count."""
    try:
        r = get_redis()
        pong = r.ping()
        info = r.dbsize()
        return {"status": "ok", "ping": pong, "key_count": info}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
