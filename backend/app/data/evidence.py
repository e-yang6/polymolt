"""
Seeded evidence for each region across all 6 sustainability categories.
Each evidence item has: id, category, title, summary, sentiment, strength (0-1).

TODO: RAG — replace this module with CategoryRetriever.retrieve() calls.
      Evidence should come from a vector store, not hardcoded dicts.
"""

from typing import TypedDict, Literal


class EvidenceItem(TypedDict):
    id: str
    category: str
    title: str
    summary: str
    sentiment: Literal["positive", "negative", "mixed"]
    strength: float  # 0.0–1.0, how strongly this evidence supports/refutes sustainability


# ─── SCANDINAVIA ─────────────────────────────────────────────────────────────

SCANDINAVIA_EVIDENCE: dict[str, list[EvidenceItem]] = {
    "climate_and_emissions": [
        {
            "id": "scan_clim_1",
            "category": "climate_and_emissions",
            "title": "Nordic carbon neutrality targets ahead of schedule",
            "summary": "Sweden and Denmark are on track to achieve net-zero before 2045, with emissions down 40% since 1990.",
            "sentiment": "positive",
            "strength": 0.88,
        },
        {
            "id": "scan_clim_2",
            "category": "climate_and_emissions",
            "title": "Norway's oil sector creates ongoing emissions tension",
            "summary": "Despite a sovereign wealth fund and EV leadership, Norway remains a major oil exporter, creating a carbon paradox.",
            "sentiment": "mixed",
            "strength": 0.55,
        },
        {
            "id": "scan_clim_3",
            "category": "climate_and_emissions",
            "title": "Carbon tax among highest in the world",
            "summary": "Sweden's carbon tax exceeds $130/tonne, the highest globally, effectively pricing fossil fuels out of the residential sector.",
            "sentiment": "positive",
            "strength": 0.85,
        },
    ],
    "energy_and_resource_systems": [
        {
            "id": "scan_energy_1",
            "category": "energy_and_resource_systems",
            "title": "98% renewable electricity in Norway",
            "summary": "Hydropower provides nearly all of Norway's electricity; Denmark leads in offshore wind capacity per capita.",
            "sentiment": "positive",
            "strength": 0.92,
        },
        {
            "id": "scan_energy_2",
            "category": "energy_and_resource_systems",
            "title": "Nordic energy grid highly interconnected",
            "summary": "The Nordpool grid enables cross-border balancing of variable renewables, achieving among the world's lowest energy waste rates.",
            "sentiment": "positive",
            "strength": 0.80,
        },
        {
            "id": "scan_energy_3",
            "category": "energy_and_resource_systems",
            "title": "EV adoption rate highest globally",
            "summary": "Norway exceeds 80% EV share in new car sales; Sweden and Denmark rapidly following with strong incentive structures.",
            "sentiment": "positive",
            "strength": 0.82,
        },
    ],
    "water_and_ecosystems": [
        {
            "id": "scan_water_1",
            "category": "water_and_ecosystems",
            "title": "Freshwater resources abundant and well-managed",
            "summary": "Nordic countries rank among the lowest in water stress globally; comprehensive watershed protection policies in place.",
            "sentiment": "positive",
            "strength": 0.85,
        },
        {
            "id": "scan_water_2",
            "category": "water_and_ecosystems",
            "title": "Baltic Sea remains ecologically stressed",
            "summary": "Despite improvements, agricultural runoff continues to cause hypoxic zones in the Baltic Sea, affecting regional biodiversity.",
            "sentiment": "negative",
            "strength": 0.55,
        },
        {
            "id": "scan_water_3",
            "category": "water_and_ecosystems",
            "title": "30% land under protected status",
            "summary": "All four Nordic countries exceed or are approaching the 30x30 biodiversity targets ahead of 2030 deadlines.",
            "sentiment": "positive",
            "strength": 0.78,
        },
    ],
    "infrastructure_and_built_environment": [
        {
            "id": "scan_infra_1",
            "category": "infrastructure_and_built_environment",
            "title": "Green building standards among world's strongest",
            "summary": "Sweden's Building Code requires near-zero energy buildings; Copenhagen has highest cycle infrastructure density per capita.",
            "sentiment": "positive",
            "strength": 0.82,
        },
        {
            "id": "scan_infra_2",
            "category": "infrastructure_and_built_environment",
            "title": "High urbanization with transit integration",
            "summary": "Over 85% urban population with well-integrated public transit; compact city planning reduces per-capita emissions.",
            "sentiment": "positive",
            "strength": 0.76,
        },
    ],
    "economy_and_social_resilience": [
        {
            "id": "scan_social_1",
            "category": "economy_and_social_resilience",
            "title": "UNDP HDI scores in top 5 globally",
            "summary": "Norway, Sweden, Denmark, and Finland consistently rank in the top 10 on Human Development Index.",
            "sentiment": "positive",
            "strength": 0.90,
        },
        {
            "id": "scan_social_2",
            "category": "economy_and_social_resilience",
            "title": "Low income inequality and strong social safety nets",
            "summary": "Gini coefficients among lowest globally; universal healthcare, education, and unemployment insurance reduce vulnerability.",
            "sentiment": "positive",
            "strength": 0.88,
        },
        {
            "id": "scan_social_3",
            "category": "economy_and_social_resilience",
            "title": "Aging population poses long-term fiscal pressure",
            "summary": "Demographic aging is straining pension and healthcare systems, though sovereign wealth funds provide substantial buffer.",
            "sentiment": "mixed",
            "strength": 0.45,
        },
    ],
    "governance_and_policy": [
        {
            "id": "scan_gov_1",
            "category": "governance_and_policy",
            "title": "Transparency International top 5 least corrupt",
            "summary": "Denmark, Finland, Sweden ranked consistently in top 5 globally for low corruption and institutional trust.",
            "sentiment": "positive",
            "strength": 0.92,
        },
        {
            "id": "scan_gov_2",
            "category": "governance_and_policy",
            "title": "NDCs submitted and policies aligned",
            "summary": "All four Nordic countries have submitted ambitious NDCs and have domestic legislation aligned with Paris Agreement targets.",
            "sentiment": "positive",
            "strength": 0.85,
        },
    ],
}

# ─── SUB-SAHARAN DROUGHT BELT ─────────────────────────────────────────────────

DROUGHT_BELT_EVIDENCE: dict[str, list[EvidenceItem]] = {
    "climate_and_emissions": [
        {
            "id": "db_clim_1",
            "category": "climate_and_emissions",
            "title": "Sahel experiencing fastest warming on Earth",
            "summary": "Temperature increases in the Sahel are 1.5x the global average; rainfall patterns increasingly erratic and unpredictable.",
            "sentiment": "negative",
            "strength": 0.90,
        },
        {
            "id": "db_clim_2",
            "category": "climate_and_emissions",
            "title": "Per capita emissions extremely low",
            "summary": "Sub-Saharan Africa contributes less than 4% of global CO2 emissions despite containing 15% of global population.",
            "sentiment": "positive",
            "strength": 0.60,
        },
        {
            "id": "db_clim_3",
            "category": "climate_and_emissions",
            "title": "Deforestation accelerating in Congo Basin",
            "summary": "The world's second-largest rainforest is losing 500,000 hectares annually, releasing significant carbon stores.",
            "sentiment": "negative",
            "strength": 0.82,
        },
    ],
    "energy_and_resource_systems": [
        {
            "id": "db_energy_1",
            "category": "energy_and_resource_systems",
            "title": "600 million people lack electricity access",
            "summary": "Sub-Saharan Africa has the world's largest energy poverty gap; 43% of population lacks reliable electricity.",
            "sentiment": "negative",
            "strength": 0.88,
        },
        {
            "id": "db_energy_2",
            "category": "energy_and_resource_systems",
            "title": "Solar potential among highest globally, underutilized",
            "summary": "The region receives among the highest solar irradiance in the world but installed capacity remains under 10 GW total.",
            "sentiment": "mixed",
            "strength": 0.55,
        },
    ],
    "water_and_ecosystems": [
        {
            "id": "db_water_1",
            "category": "water_and_ecosystems",
            "title": "Severe water stress in 14 countries",
            "summary": "Lake Chad has shrunk 90% since 1963; groundwater depletion accelerating in Ethiopia, Kenya, and Somalia.",
            "sentiment": "negative",
            "strength": 0.92,
        },
        {
            "id": "db_water_2",
            "category": "water_and_ecosystems",
            "title": "2 billion people at risk from drought by 2030",
            "summary": "IPCC projections show the Sahel region faces 50% probability of multi-year drought events by 2030.",
            "sentiment": "negative",
            "strength": 0.88,
        },
        {
            "id": "db_water_3",
            "category": "water_and_ecosystems",
            "title": "Desertification advancing 48 km/year southward",
            "summary": "The Sahara-Sahel boundary continues to advance despite the Great Green Wall initiative.",
            "sentiment": "negative",
            "strength": 0.85,
        },
    ],
    "infrastructure_and_built_environment": [
        {
            "id": "db_infra_1",
            "category": "infrastructure_and_built_environment",
            "title": "Infrastructure deficit estimated at $150B annually",
            "summary": "African Development Bank estimates the continent needs $130–170B per year in infrastructure investment; current spending is far below this.",
            "sentiment": "negative",
            "strength": 0.80,
        },
        {
            "id": "db_infra_2",
            "category": "infrastructure_and_built_environment",
            "title": "Urban slum population growing rapidly",
            "summary": "60% of urban sub-Saharan African population lives in informal settlements with limited services and high flood risk.",
            "sentiment": "negative",
            "strength": 0.82,
        },
    ],
    "economy_and_social_resilience": [
        {
            "id": "db_social_1",
            "category": "economy_and_social_resilience",
            "title": "Food insecurity affects 250 million people",
            "summary": "WFP data shows 250M people acutely food insecure in sub-Saharan Africa, with 70M in emergency-level hunger.",
            "sentiment": "negative",
            "strength": 0.90,
        },
        {
            "id": "db_social_2",
            "category": "economy_and_social_resilience",
            "title": "Youth dividend: 60% of population under 25",
            "summary": "The continent's large youth population represents potential for future growth if education and employment systems develop adequately.",
            "sentiment": "mixed",
            "strength": 0.40,
        },
    ],
    "governance_and_policy": [
        {
            "id": "db_gov_1",
            "category": "governance_and_policy",
            "title": "Governance fragility in Sahel region",
            "summary": "Multiple coup d'états in Mali, Burkina Faso, Niger since 2021; governance fragility undermines climate adaptation capacity.",
            "sentiment": "negative",
            "strength": 0.85,
        },
        {
            "id": "db_gov_2",
            "category": "governance_and_policy",
            "title": "NDC submissions incomplete or non-binding",
            "summary": "Most Sahel countries have submitted NDCs but lack domestic enforcement mechanisms or finance to implement them.",
            "sentiment": "negative",
            "strength": 0.75,
        },
    ],
}

# ─── INDUSTRIAL DELTA (PEARL RIVER) ──────────────────────────────────────────
# Tuned for Phase 2: genuine category-level disagreement.
# Environment categories (climate, energy, water) → strongly negative → Climate/Water/Env agents sell hard.
# Human-systems categories (infra, social, governance) → strongly positive → Infra/Social/Human agents buy hard.
# Master Generalist sees all → net slightly negative → mild sell pressure.
# This produces persistent oscillation in the 40–60% range.

INDUSTRIAL_DELTA_EVIDENCE: dict[str, list[EvidenceItem]] = {
    "climate_and_emissions": [
        {
            "id": "id_clim_1",
            "category": "climate_and_emissions",
            "title": "PRD carbon intensity among Asia's worst",
            "summary": "Manufacturing and freight sectors make the Pearl River Delta one of Asia's most carbon-intensive regions per km²; annual emissions exceed 600MtCO₂e.",
            "sentiment": "negative",
            "strength": 0.90,
        },
        {
            "id": "id_clim_2",
            "category": "climate_and_emissions",
            "title": "Guangdong ETS operational but carbon price below $12/tonne",
            "summary": "China's largest regional carbon market covers the PRD but the carbon price remains far below levels needed to drive deep decarbonization.",
            "sentiment": "negative",
            "strength": 0.68,
        },
        {
            "id": "id_clim_3",
            "category": "climate_and_emissions",
            "title": "China net-zero 2060 pledge includes Guangdong",
            "summary": "Guangdong has adopted provincial emission peak targets, but credibility depends on enforcement mechanisms still being developed.",
            "sentiment": "mixed",
            "strength": 0.45,
        },
    ],
    "energy_and_resource_systems": [
        {
            "id": "id_energy_1",
            "category": "energy_and_resource_systems",
            "title": "Grid 54% coal-dependent despite solar manufacturing leadership",
            "summary": "Guangdong produces 40% of global solar panels but its own electricity grid remains majority fossil fuel; renewables are an export product, not a local solution.",
            "sentiment": "negative",
            "strength": 0.82,
        },
        {
            "id": "id_energy_2",
            "category": "energy_and_resource_systems",
            "title": "Absolute energy consumption still rising year-on-year",
            "summary": "Despite a 30% reduction in energy intensity per unit of GDP, total energy consumption continues to grow as manufacturing scales faster than efficiency gains.",
            "sentiment": "negative",
            "strength": 0.72,
        },
    ],
    "water_and_ecosystems": [
        {
            "id": "id_water_1",
            "category": "water_and_ecosystems",
            "title": "Pearl River toxic heavy metal contamination widespread",
            "summary": "Industrial discharge has caused severe heavy metal and microplastic contamination across 400+ km of the Pearl River; aquatic biodiversity collapse in lower reaches.",
            "sentiment": "negative",
            "strength": 0.92,
        },
        {
            "id": "id_water_2",
            "category": "water_and_ecosystems",
            "title": "Mangrove cover down 65% since 1980",
            "summary": "Coastal urbanization has eliminated two-thirds of Pearl River Delta mangroves, removing critical carbon sinks and storm-surge protection for 30M coastal residents.",
            "sentiment": "negative",
            "strength": 0.88,
        },
        {
            "id": "id_water_3",
            "category": "water_and_ecosystems",
            "title": "Blue Sky initiative showing early improvements",
            "summary": "Guangdong's clean-water enforcement program achieved 15% reduction in industrial discharge violations since 2020, though absolute pollution levels remain high.",
            "sentiment": "positive",
            "strength": 0.42,
        },
    ],
    "infrastructure_and_built_environment": [
        {
            "id": "id_infra_1",
            "category": "infrastructure_and_built_environment",
            "title": "World-class transit: HSR, metro, and full EV bus fleet",
            "summary": "Guangzhou-Shenzhen high-speed rail corridor is the world's busiest; Shenzhen operates the world's largest fully-electric bus fleet of 16,000 vehicles.",
            "sentiment": "positive",
            "strength": 0.90,
        },
        {
            "id": "id_infra_2",
            "category": "infrastructure_and_built_environment",
            "title": "Shenzhen smart-city infrastructure globally ranked",
            "summary": "Shenzhen ranks top-10 globally for smart-city infrastructure, digital services, and urban logistics efficiency — a model for sustainable urban systems.",
            "sentiment": "positive",
            "strength": 0.82,
        },
        {
            "id": "id_infra_3",
            "category": "infrastructure_and_built_environment",
            "title": "40 million residents in high compound flood-risk zones",
            "summary": "Sea level rise and intensifying typhoons threaten the PRD's low-lying coastal cities; adaptation infrastructure investment is accelerating but lagging risk growth.",
            "sentiment": "negative",
            "strength": 0.65,
        },
    ],
    "economy_and_social_resilience": [
        {
            "id": "id_social_1",
            "category": "economy_and_social_resilience",
            "title": "PRD GDP exceeds $2.4 trillion — top 10 regional economy",
            "summary": "The Pearl River Delta is one of the world's wealthiest and most economically resilient regions; Shenzhen's tech sector, Guangzhou manufacturing, and Macau tourism create robust diversification.",
            "sentiment": "positive",
            "strength": 0.92,
        },
        {
            "id": "id_social_2",
            "category": "economy_and_social_resilience",
            "title": "Rapid poverty reduction and growing middle class",
            "summary": "Guangdong lifted 6 million rural residents out of poverty in the 2015–2020 period; middle-class consumption now drives resilience against external shocks.",
            "sentiment": "positive",
            "strength": 0.80,
        },
        {
            "id": "id_social_3",
            "category": "economy_and_social_resilience",
            "title": "30 million internal migrants lack full social protections",
            "summary": "The hukou system limits migrants' access to education, healthcare, and pension rights, creating vulnerability beneath the headline economic strength.",
            "sentiment": "negative",
            "strength": 0.68,
        },
    ],
    "governance_and_policy": [
        {
            "id": "id_gov_1",
            "category": "governance_and_policy",
            "title": "Strong state capacity delivers large-scale policy execution",
            "summary": "Guangdong demonstrates high state capacity for rapid infrastructure deployment and policy implementation — the EV mandate, transit investment, and clean-water enforcement are tangible examples.",
            "sentiment": "positive",
            "strength": 0.75,
        },
        {
            "id": "id_gov_2",
            "category": "governance_and_policy",
            "title": "Environmental enforcement inconsistent outside showcase cities",
            "summary": "While Shenzhen and Guangzhou show strong compliance, environmental enforcement in second-tier PRD cities and industrial zones remains selective and politically constrained.",
            "sentiment": "negative",
            "strength": 0.70,
        },
        {
            "id": "id_gov_3",
            "category": "governance_and_policy",
            "title": "Greater Bay Area plan integrates sustainability targets",
            "summary": "The Guangdong-Hong Kong-Macao Greater Bay Area framework includes explicit sustainability indicators and inter-city environmental coordination mechanisms.",
            "sentiment": "positive",
            "strength": 0.60,
        },
    ],
}

# ─── Evidence registry ─────────────────────────────────────────────────────────

EVIDENCE_REGISTRY: dict[str, dict[str, list[EvidenceItem]]] = {
    "scandinavia": SCANDINAVIA_EVIDENCE,
    "drought_belt": DROUGHT_BELT_EVIDENCE,
    "industrial_delta": INDUSTRIAL_DELTA_EVIDENCE,
}


def get_evidence(region_id: str, category: str) -> list[EvidenceItem]:
    """
    Returns evidence items for a given region and category.
    TODO: RAG — replace this function with CategoryRetriever.retrieve(region_id, category)
    """
    region_evidence = EVIDENCE_REGISTRY.get(region_id, {})
    return region_evidence.get(category, [])


def get_all_evidence(region_id: str) -> dict[str, list[EvidenceItem]]:
    """Returns all evidence for a region, keyed by category."""
    return EVIDENCE_REGISTRY.get(region_id, {})
