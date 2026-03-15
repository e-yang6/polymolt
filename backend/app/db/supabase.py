"""
Supabase-backed persistence for questions and stakeholder AI perspectives.

This mirrors the public interface of `app.db.db2` so that the rest of the
application (routers, orchestration) can switch between backends without
code changes elsewhere.

Assumed Postgres schema (create these in your Supabase project):

  -- Questions table
  create table public.questions (
    id            bigint generated always as identity primary key,
    question_text text    not null,
    location      text    not null,
    created_at    timestamptz not null default now()
  );

  -- Stakeholder responses table
  create table public.stakeholder_responses (
    id                bigint generated always as identity primary key,
    question_id       bigint      not null references public.questions(id) on delete cascade,
    phase             text        not null default 'legacy',
    stakeholder_id    text        not null,
    stakeholder_role  text        not null,
    ai_agent_id       text        not null,
    answer            text        not null,
    confidence        double precision,
    reasoning         text,
    raw_payload       jsonb,
    created_at        timestamptz not null default now()
  );

  -- Orchestrate runs table
  create table public.orchestrate_runs (
    id                bigint generated always as identity primary key,
    question_id       bigint      not null references public.questions(id) on delete cascade,
    topic_reasoning   text,
    deep_analysis     text,
    assigned_agent_id text,
    expertise_rationale text,
    rag_context       text,
    context_for_agents text,
    year              integer,
    model             text,
    full_response     jsonb,
    created_at        timestamptz not null default now()
  );
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Iterable, Literal

from supabase import Client, create_client

from app.cache import NS_DB, cache_get, cache_invalidate_namespace, cache_set, TTL_DB_READ


def _get_client() -> Client:
  url = os.getenv("SUPABASE_URL")
  key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
  if not url or not key:
    raise RuntimeError(
      "Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in backend/.env."
    )
  return create_client(url.rstrip("/"), key.strip())


_client: Client | None = None


def _client_singleton() -> Client:
  global _client
  if _client is None:
    _client = _get_client()
  return _client


@dataclass
class StakeholderPerspective:
  """Single stakeholder AI response for a question."""

  stakeholder_id: str
  stakeholder_role: str
  ai_agent_id: str
  answer: Literal["yes", "no"]
  confidence: float | None = None
  reasoning: str | None = None
  location: str | None = None
  raw_payload: dict[str, Any] | None = None


@dataclass
class QuestionSummary:
  """Lightweight view of a question with simple yes/no counts."""

  id: int
  question_text: str
  location: str
  created_at: str
  yes_count: int
  no_count: int


@dataclass
class QuestionRow:
  """Full question row without aggregated counts."""

  id: int
  question_text: str
  location: str
  created_at: str


@dataclass
class StakeholderResponseRow:
  """Single stored stakeholder response row."""

  id: int
  question_id: int
  phase: str
  stakeholder_id: str
  stakeholder_role: str
  ai_agent_id: str
  answer: str
  confidence: float | None
  reasoning: str | None
  created_at: str


def _invalidate_db_cache() -> None:
  """Clear all DB read caches after a write operation."""
  cache_invalidate_namespace(NS_DB)


def _insert_question(question: str, location: str) -> int:
  client = _client_singleton()
  resp = client.table("questions").insert(
    {"question_text": question, "location": location}
  ).execute()
  data = getattr(resp, "data", None) or []
  if not data or "id" not in data[0]:
    raise RuntimeError("Failed to insert question into Supabase.")
  return int(data[0]["id"])


def create_question_only(question: str, location: str) -> int:
  """
  Create a question row without any stakeholder responses.
  """
  qid = _insert_question(question, location)
  _invalidate_db_cache()
  return qid


def save_question_with_perspectives(
  question: str,
  location: str,
  perspectives: list[StakeholderPerspective],
) -> int:
  """
  Persist a single user question and all stakeholder AI perspectives.
  """
  client = _client_singleton()
  question_id = _insert_question(question, location)

  if perspectives:
    rows: list[dict[str, Any]] = []
    for p in perspectives:
      answer_normalized = p.answer.lower()
      if answer_normalized not in {"yes", "no"}:
        raise ValueError(f"Invalid answer value: {p.answer!r}")
      answer_db = "YES" if answer_normalized == "yes" else "NO"
      rows.append(
        {
          "question_id": question_id,
          "phase": "legacy",
          "stakeholder_id": p.stakeholder_id,
          "stakeholder_role": p.stakeholder_role,
          "ai_agent_id": p.ai_agent_id,
          "answer": answer_db,
          "confidence": p.confidence,
          "reasoning": p.reasoning,
          "raw_payload": p.raw_payload,
        }
      )
    client.table("stakeholder_responses").insert(rows).execute()

  _invalidate_db_cache()
  return question_id


def list_recent_questions(limit: int = 50) -> list[QuestionSummary]:
  """
  Return most recent questions with simple yes/no counts. Cached in Redis.
  """
  cache_key_parts: Iterable[Any] = ("list_recent_questions_supabase", limit)
  cached = cache_get(NS_DB, *cache_key_parts)
  if cached is not None:
    return [QuestionSummary(**row) for row in cached]

  client = _client_singleton()
  q_resp = client.table("questions").select(
    "id, question_text, location, created_at"
  ).order("created_at", desc=True).limit(limit).execute()
  q_rows = getattr(q_resp, "data", None) or []
  ids = [int(q["id"]) for q in q_rows]

  yes_no_by_qid: dict[int, tuple[int, int]] = {}
  if ids:
    r_resp = (
      client.table("stakeholder_responses")
      .select("question_id, answer")
      .in_("question_id", ids)
      .execute()
    )
    r_rows = getattr(r_resp, "data", None) or []
    for r in r_rows:
      qid = int(r["question_id"])
      ans = str(r["answer"]).upper()
      yes, no = yes_no_by_qid.get(qid, (0, 0))
      if ans == "YES":
        yes += 1
      elif ans == "NO":
        no += 1
      yes_no_by_qid[qid] = (yes, no)

  results: list[QuestionSummary] = []
  for q in q_rows:
    qid = int(q["id"])
    yes, no = yes_no_by_qid.get(qid, (0, 0))
    results.append(
      QuestionSummary(
        id=qid,
        question_text=str(q["question_text"]),
        location=str(q["location"]),
        created_at=str(q.get("created_at", "")),
        yes_count=yes,
        no_count=no,
      )
    )

  serializable = [
    {
      "id": r.id,
      "question_text": r.question_text,
      "location": r.location,
      "created_at": r.created_at,
      "yes_count": r.yes_count,
      "no_count": r.no_count,
    }
    for r in results
  ]
  cache_set(NS_DB, *cache_key_parts, value=serializable, ttl=TTL_DB_READ)
  return results


def get_question_with_responses(
  question_id: int,
) -> tuple[QuestionRow, list[StakeholderResponseRow]]:
  """
  Load a single question and all of its stakeholder responses. Cached in Redis.
  """
  cache_key_parts: Iterable[Any] = ("get_question_with_responses_supabase", question_id)
  cached = cache_get(NS_DB, *cache_key_parts)
  if cached is not None:
    q_data, resp_data = cached["question"], cached["responses"]
    question = QuestionRow(**q_data)
    responses = [StakeholderResponseRow(**r) for r in resp_data]
    return question, responses

  client = _client_singleton()
  q_resp = (
    client.table("questions")
    .select("id, question_text, location, created_at")
    .eq("id", question_id)
    .limit(1)
    .execute()
  )
  q_rows = getattr(q_resp, "data", None) or []
  if not q_rows:
    raise ValueError(f"Question {question_id} not found.")
  q_row = q_rows[0]
  question = QuestionRow(
    id=int(q_row["id"]),
    question_text=str(q_row["question_text"]),
    location=str(q_row["location"]),
    created_at=str(q_row.get("created_at", "")),
  )

  r_resp = (
    client.table("stakeholder_responses")
    .select(
      "id, question_id, phase, stakeholder_id, stakeholder_role, ai_agent_id, answer, confidence, reasoning, created_at"
    )
    .eq("question_id", question_id)
    .order("created_at", desc=False)
    .order("id", desc=False)
    .execute()
  )
  r_rows = getattr(r_resp, "data", None) or []
  responses: list[StakeholderResponseRow] = []
  for r in r_rows:
    confidence_val = r.get("confidence")
    confidence = float(confidence_val) if confidence_val is not None else None
    responses.append(
      StakeholderResponseRow(
        id=int(r["id"]),
        question_id=int(r["question_id"]),
        phase=str(r.get("phase") or "legacy"),
        stakeholder_id=str(r["stakeholder_id"]),
        stakeholder_role=str(r["stakeholder_role"]),
        ai_agent_id=str(r["ai_agent_id"]),
        answer=str(r["answer"]),
        confidence=confidence,
        reasoning=str(r.get("reasoning")) if r.get("reasoning") is not None else None,
        created_at=str(r.get("created_at", "")),
      )
    )

  serializable = {
    "question": {
      "id": question.id,
      "question_text": question.question_text,
      "location": question.location,
      "created_at": question.created_at,
    },
    "responses": [
      {
        "id": r.id,
        "question_id": r.question_id,
        "phase": r.phase,
        "stakeholder_id": r.stakeholder_id,
        "stakeholder_role": r.stakeholder_role,
        "ai_agent_id": r.ai_agent_id,
        "answer": r.answer,
        "confidence": r.confidence,
        "reasoning": r.reasoning,
        "created_at": r.created_at,
      }
      for r in responses
    ],
  }
  cache_set(NS_DB, *cache_key_parts, value=serializable, ttl=TTL_DB_READ)
  return question, responses


@dataclass
class OrchestrateRunRow:
  """One row from orchestrate_runs."""

  id: int
  question_id: int
  topic_reasoning: str
  deep_analysis: str
  assigned_agent_id: str | None
  expertise_rationale: str | None
  rag_context: str | None
  context_for_agents: str | None
  year: int | None
  model: str | None
  full_response: str | None
  created_at: str


def save_orchestrate_response(
  question: str,
  location: str,
  response: dict[str, Any],
  year: int | None = None,
  model: str | None = None,
) -> int:
  """
  Save a full /ai/orchestrate response to Supabase under one question.
  """
  client = _client_singleton()
  question_id = _insert_question(question, location)

  topic_reasoning = response.get("topic_reasoning") or ""
  deep_analysis = response.get("deep_analysis") or ""
  assigned_agent_id = response.get("assigned_agent_id") or ""
  expertise_rationale = response.get("expertise_rationale") or ""
  context_for_agents = response.get("context_for_agents") or ""

  client.table("orchestrate_runs").insert(
    {
      "question_id": question_id,
      "topic_reasoning": topic_reasoning,
      "deep_analysis": deep_analysis,
      "assigned_agent_id": assigned_agent_id or None,
      "expertise_rationale": expertise_rationale,
      "rag_context": context_for_agents,
      "context_for_agents": context_for_agents,
      "year": year,
      "model": (model or "") or None,
      "full_response": response,
    }
  ).execute()

  # initial_bets
  initial_bets = response.get("initial_bets") or []
  for bet in initial_bets:
    answer = (bet.get("answer") or "UNKNOWN").strip().upper()
    if answer not in ("YES", "NO"):
      answer = "NO"
    client.table("stakeholder_responses").insert(
      {
        "question_id": question_id,
        "phase": "initial_bet",
        "stakeholder_id": bet.get("agent_id") or "",
        "stakeholder_role": bet.get("agent_name") or "",
        "ai_agent_id": bet.get("agent_id") or "",
        "answer": answer,
        "confidence": bet.get("confidence"),
        "reasoning": (bet.get("reasoning") or "")[:32700],
        "raw_payload": None,
      }
    ).execute()

  # triggered_agents
  triggered = response.get("triggered_agents") or []
  for t in triggered:
    answer = (t.get("answer") or "UNKNOWN").strip().upper()
    if answer not in ("YES", "NO"):
      answer = "NO"
    raw = {"choice_reasoning": t.get("choice_reasoning") or ""}
    client.table("stakeholder_responses").insert(
      {
        "question_id": question_id,
        "phase": "triggered",
        "stakeholder_id": t.get("agent_id") or "",
        "stakeholder_role": t.get("agent_name") or "",
        "ai_agent_id": t.get("agent_id") or "",
        "answer": answer,
        "confidence": None,
        "reasoning": None,
        "raw_payload": raw,
      }
    ).execute()

  # second_bets
  choice_reasoning_by_id = {
    t.get("agent_id"): t.get("choice_reasoning", "") for t in triggered
  }
  second_bets = response.get("second_bets") or []
  for sb in second_bets:
    answer = (sb.get("answer") or "UNKNOWN").strip().upper()
    if answer not in ("YES", "NO"):
      answer = "NO"
    aid = sb.get("agent_id") or ""
    raw = {"choice_reasoning": choice_reasoning_by_id.get(aid, "")}
    client.table("stakeholder_responses").insert(
      {
        "question_id": question_id,
        "phase": "second_bet",
        "stakeholder_id": aid,
        "stakeholder_role": sb.get("agent_name") or "",
        "ai_agent_id": aid,
        "answer": answer,
        "confidence": sb.get("confidence"),
        "reasoning": (sb.get("reasoning") or "")[:32700],
        "raw_payload": raw,
      }
    ).execute()

  _invalidate_db_cache()
  return question_id


def get_orchestrate_run(question_id: int) -> OrchestrateRunRow | None:
  """Load the orchestrate run for a question, if any. Cached in Redis."""
  cache_key_parts: Iterable[Any] = ("get_orchestrate_run_supabase", question_id)
  cached = cache_get(NS_DB, *cache_key_parts)
  if cached is not None:
    return OrchestrateRunRow(**cached) if cached != "__none__" else None

  client = _client_singleton()
  resp = (
    client.table("orchestrate_runs")
    .select(
      "id, question_id, topic_reasoning, deep_analysis, assigned_agent_id, expertise_rationale, rag_context, context_for_agents, year, model, full_response, created_at"
    )
    .eq("question_id", question_id)
    .order("created_at", desc=True)
    .limit(1)
    .execute()
  )
  rows = getattr(resp, "data", None) or []
  if not rows:
    cache_set(NS_DB, *cache_key_parts, value="__none__", ttl=TTL_DB_READ)
    return None
  row = rows[0]
  result = OrchestrateRunRow(
    id=int(row["id"]),
    question_id=int(row["question_id"]),
    topic_reasoning=str(row.get("topic_reasoning") or ""),
    deep_analysis=str(row.get("deep_analysis") or ""),
    assigned_agent_id=str(row["assigned_agent_id"]) if row.get("assigned_agent_id") else None,
    expertise_rationale=str(row["expertise_rationale"]) if row.get("expertise_rationale") else None,
    rag_context=str(row["rag_context"]) if row.get("rag_context") else None,
    context_for_agents=str(row["context_for_agents"]) if row.get("context_for_agents") else None,
    year=int(row["year"]) if row.get("year") is not None else None,
    model=str(row["model"]) if row.get("model") else None,
    full_response=json.dumps(row.get("full_response")) if row.get("full_response") is not None else None,
    created_at=str(row.get("created_at", "")),
  )
  serializable = {
    "id": result.id,
    "question_id": result.question_id,
    "topic_reasoning": result.topic_reasoning,
    "deep_analysis": result.deep_analysis,
    "assigned_agent_id": result.assigned_agent_id,
    "expertise_rationale": result.expertise_rationale,
    "rag_context": result.rag_context,
    "context_for_agents": result.context_for_agents,
    "year": result.year,
    "model": result.model,
    "full_response": result.full_response,
    "created_at": result.created_at,
  }
  cache_set(NS_DB, *cache_key_parts, value=serializable, ttl=TTL_DB_READ)
  return result

