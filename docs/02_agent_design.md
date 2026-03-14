# Agent Design

## Overview

9 agents trade on the sustainability market. Their structure, knowledge access, and behavioral traits are fixed at initialization but their beliefs, positions, and reasoning evolve as they observe evidence and market price.

---

## Agent Roster

### Specialists (6) — Betting Power: 1.0x

| ID | Name | Categories |
|----|------|-----------|
| `climate` | Climate Agent | climate_and_emissions |
| `energy` | Energy Agent | energy_and_resource_systems |
| `water` | Water & Ecosystem Agent | water_and_ecosystems |
| `infrastructure` | Infrastructure Agent | infrastructure_and_built_environment |
| `social` | Social Resilience Agent | economy_and_social_resilience |
| `governance` | Governance Agent | governance_and_policy |

### Hybrids (2) — Betting Power: 1.5x

| ID | Name | Categories |
|----|------|-----------|
| `env_generalist` | Environmental Generalist | climate_and_emissions, energy_and_resource_systems, water_and_ecosystems |
| `human_generalist` | Human Systems Generalist | infrastructure_and_built_environment, economy_and_social_resilience, governance_and_policy |

### Master Generalist (1) — Betting Power: 2.0x

| ID | Name | Categories |
|----|------|-----------|
| `master` | Master Generalist | All 6 categories |

---

## Agent Data Structure

```python
@dataclass
class Agent:
    id: str
    name: str
    agent_type: Literal["specialist", "hybrid", "master"]
    categories: list[str]           # corpus names accessible
    betting_power: float            # 1.0, 1.5, or 2.0

    # Behavior traits (0.0–1.0 scale unless noted)
    confidence: float               # how strongly they act on beliefs
    risk_tolerance: float           # willingness to take large positions
    stubbornness: float             # resistance to updating on price movement
    herd_sensitivity: float         # tendency to follow market direction
    update_frequency: float         # how often they recalculate (0=slow, 1=fast)
    contrarian: bool                # if True, trades against consensus

    # Dynamic state
    current_belief: float           # private probability estimate (0–1)
    current_position: float         # net position (+long, -short)
    last_reasoning: str             # latest explanation string
    evidence_used: list[dict]       # evidence items referenced in last reasoning
    trade_history: list[dict]       # recent trades
```

---

## Default Behavior Trait Profiles

| Agent | Confidence | Risk Tol. | Stubborn | Herd | Freq | Contrarian |
|-------|-----------|-----------|---------|------|------|------------|
| Climate | 0.85 | 0.6 | 0.7 | 0.2 | 0.8 | False |
| Energy | 0.80 | 0.65 | 0.6 | 0.25 | 0.7 | False |
| Water | 0.75 | 0.5 | 0.65 | 0.3 | 0.75 | False |
| Infrastructure | 0.70 | 0.7 | 0.5 | 0.35 | 0.65 | False |
| Social Resilience | 0.65 | 0.55 | 0.4 | 0.5 | 0.6 | False |
| Governance | 0.72 | 0.6 | 0.55 | 0.4 | 0.7 | False |
| Env. Generalist | 0.68 | 0.7 | 0.35 | 0.45 | 0.85 | False |
| Human Generalist | 0.65 | 0.65 | 0.3 | 0.5 | 0.8 | False |
| Master Generalist | 0.60 | 0.75 | 0.2 | 0.6 | 0.9 | False |

Note: Master Generalist has lower stubbornness — more willing to update on new evidence. High herd sensitivity reflects awareness of aggregate signals.

---

## Belief Formation

Each agent forms a private belief as follows:

1. **Read evidence** from their accessible categories
2. **Score each evidence item** (positive/negative, strength 0–1)
3. **Compute raw belief** = weighted average of scored evidence
4. **Apply stubbornness**: blend raw belief with prior belief based on `stubbornness`
5. **Apply herd adjustment**: nudge belief toward market price based on `herd_sensitivity`

```
adjusted_belief = (
    raw_evidence_belief * (1 - stubbornness) +
    prior_belief * stubbornness
)
final_belief = (
    adjusted_belief * (1 - herd_sensitivity) +
    market_price * herd_sensitivity
)
```

Note: Contrarian agents invert the herd adjustment (nudge *away* from market).

---

## Trade Decision

Trade size calculation:

```
base_size = betting_power * confidence * risk_tolerance
belief_gap = abs(private_belief - market_price)
evidence_factor = mean(evidence_strength for evidence in used_evidence)
trade_size = base_size * belief_gap * evidence_factor
direction = BUY if private_belief > market_price else SELL
```

An agent skips a trade if:
- `belief_gap < 0.02` (too close to market to act)
- `update_frequency` check fails (random skip based on frequency)

---

## Reasoning Generation

Each agent generates a short explanation combining:
- The top 2–3 evidence items that drove the belief
- The direction and magnitude of their position change
- A reference to the gap between their belief and market price

In MVP: templated reasoning strings using evidence titles and scores.
Future: LLM-generated reasoning via Langflow workflow.

---

## Knowledge Asymmetry Design

The power of this system comes from structural ignorance:

- The **Climate Agent** knows exactly what emissions look like but has no idea about governance
- The **Governance Agent** knows policy strength but may miss water stress
- The **Master Generalist** sees everything but acts with less conviction per category

This means specialists can move the market in their domain even when the generalist disagrees — because the specialist's evidence is more specific and their conviction is higher.

---

## Evolution Over Time

Agents update beliefs on a schedule determined by `update_frequency`:
- High frequency agents update every round
- Low frequency agents may skip rounds
- Belief evolution is logged to `trade_history` for inspection in the UI
