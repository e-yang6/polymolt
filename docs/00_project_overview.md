# Polymolt — Project Overview

## Vision

Polymolt is a **real-time AI prediction market** for regional sustainability. The core insight: sustainability is not a score — it's a contested signal that emerges from agents with different knowledge, different beliefs, and different behaviors trading against each other.

The question is always: **"Is this region sustainable?"**

The answer is always: **the current market probability.**

## Why This Is Different

Most sustainability tools produce a number from a formula. Polymolt produces a probability from a market.

The difference:
- **Disagreement is visible** — specialists can contest generalists
- **Evidence asymmetry is structural** — a climate agent knows things a governance agent doesn't
- **Behavior drives dynamics** — a stubborn agent and a herd-follower produce different markets
- **No convergence is guaranteed** — the market can stay contested

This makes Polymolt both a product and a research instrument.

## What Users See

1. Select a region (or use a seeded demo)
2. Watch the probability chart update in real time as agents trade
3. Read the trade feed: who traded, why, how big, what changed
4. Click an agent card to inspect its knowledge, reasoning, evidence, and traits
5. Compare how the same market behaves for a sustainable vs. contested region

## Research Angle

Polymolt is also a study of **LLM-like behavior under asymmetric information**:
- Does a master generalist drown out specialists?
- Does herd behavior produce bubbles?
- Do contrarian agents stabilize or destabilize markets?
- How does evidence breadth vs. evidence depth trade off?

## Demo Regions

| Region | Profile | Expected Market Behavior |
|--------|---------|--------------------------|
| Scandinavia (Nordic Model) | Strongly sustainable | Fast convergence to high probability, mild disagreement |
| Sub-Saharan Drought Belt | Weak across categories | Convergence to low probability, high specialist certainty |
| Industrial Delta (Pearl River) | Mixed — strong economy, weak environment | Persistent disagreement, contested probability, volatile chart |

## Scope

This is a **hackathon MVP**. The goal is a working, demo-ready local app that:
- Feels like a real prediction market
- Shows visibly different behavior across regions
- Makes agent reasoning legible to a non-technical observer
- Is architecturally ready for real RAG/Langflow integration
