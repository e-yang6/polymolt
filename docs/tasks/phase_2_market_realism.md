# Phase 2 Tasks — Market Realism

## Goal
Make agent behavior distinctly different and market dynamics more interesting and defensible.

## Tasks

### B2.1 — Belief Persistence
- [ ] Agents maintain belief across rounds (no full reset)
- [ ] Prior belief is updated, not replaced, each round
- [ ] Stubbornness trait controls how much the prior is weighted

### B2.2 — Momentum Awareness
- [ ] Track price direction in MarketState (rising/falling/stable)
- [ ] Agents with high herd_sensitivity adjust belief based on price momentum
- [ ] Add `price_momentum` field to MarketState

### B2.3 — Position Limits
- [ ] Each agent has a max_position cap (configurable per type)
- [ ] Agent will not trade if position is at cap in trade direction
- [ ] This prevents any single agent from dominating indefinitely

### B2.4 — Confidence Decay
- [ ] Without new confirming evidence, agent confidence decays each round
- [ ] Decay rate configurable per agent
- [ ] Confidence floors at 0.3 (agents never become totally passive)

### B2.5 — Contrarian Logic
- [ ] Add `contrarian: bool` field to Agent
- [ ] Contrarian agents invert their herd adjustment
- [ ] Default: no agents are contrarian in MVP, but trait is available
- [ ] Can be set per-region for interesting dynamics

### B2.6 — Stronger Reasoning Templates
- [ ] Reasoning templates reference specific evidence titles and strengths
- [ ] Include comparison to market price in explanation
- [ ] Format: "Given [evidence1] and [evidence2], I estimate P=X%. Market says Y%. I'm [buying/selling]."

### B2.7 — Region Tuning
- [ ] Review all 3 seeded regions against market behavior goals
- [ ] Adjust evidence strengths so regions produce distinct dynamics
- [ ] Document expected behavior per region in evidence file

## Acceptance Criteria
- [ ] Industrial Delta shows persistent disagreement (probability oscillates in 40–65% range)
- [ ] Scandinavia converges to 70–85% within 20 trades
- [ ] Sub-Saharan Drought Belt converges to 20–35%
- [ ] Agent trade history shows varying patterns (not all agents trade equally)
- [ ] Reasoning text references specific evidence items
