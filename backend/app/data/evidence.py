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

INDUSTRIAL_DELTA_EVIDENCE: dict[str, list[EvidenceItem]] = {
    "climate_and_emissions": [
        {
            "id": "id_clim_1",
            "category": "climate_and_emissions",
            "title": "Pearl River Delta among Asia's highest emission zones",
            "summary": "The PRD's manufacturing and logistics sectors make it one of the most carbon-intensive regions per km² globally.",
            "sentiment": "negative",
            "strength": 0.85,
        },
        {
            "id": "id_clim_2",
            "category": "climate_and_emissions",
            "title": "China's 2060 carbon neutrality target includes PRD",
            "summary": "Guangdong province has committed to peaking emissions by 2025 and has launched the largest regional ETS in China.",
            "sentiment": "positive",
            "strength": 0.65,
        },
    ],
    "energy_and_resource_systems": [
        {
            "id": "id_energy_1",
            "category": "energy_and_resource_systems",
            "title": "Massive solar manufacturing, modest local deployment",
            "summary": "Guangdong manufactures 40% of global solar panels but its own grid remains heavily coal-dependent (52% coal share).",
            "sentiment": "mixed",
            "strength": 0.72,
        },
        {
            "id": "id_energy_2",
            "category": "energy_and_resource_systems",
            "title": "Energy intensity declining but still high",
            "summary": "GDP energy intensity has fallen 30% since 2010, but absolute energy consumption continues to rise with economic growth.",
            "sentiment": "mixed",
            "strength": 0.60,
        },
    ],
    "water_and_ecosystems": [
        {
            "id": "id_water_1",
            "category": "water_and_ecosystems",
            "title": "Pearl River severe industrial pollution",
            "summary": "Heavy metal contamination and chemical discharge have rendered significant stretches of the Pearl River unsafe for aquatic life.",
            "sentiment": "negative",
            "strength": 0.88,
        },
        {
            "id": "id_water_2",
            "category": "water_and_ecosystems",
            "title": "Mangrove loss 60% since 1980",
            "summary": "Coastal development has destroyed over 60% of Pearl River Delta mangroves, eliminating critical storm surge buffers.",
            "sentiment": "negative",
            "strength": 0.85,
        },
        {
            "id": "id_water_3",
            "category": "water_and_ecosystems",
            "title": "Guangdong cleaning up river under Blue Sky initiative",
            "summary": "The Blue Sky, Clear Water initiative has resulted in measurable improvements in air and water quality in Guangzhou since 2018.",
            "sentiment": "positive",
            "strength": 0.55,
        },
    ],
    "infrastructure_and_built_environment": [
        {
            "id": "id_infra_1",
            "category": "infrastructure_and_built_environment",
            "title": "World-class transport infrastructure",
            "summary": "Guangzhou-Shenzhen corridor has the densest high-speed rail network globally; Shenzhen has fully electrified its bus fleet.",
            "sentiment": "positive",
            "strength": 0.82,
        },
        {
            "id": "id_infra_2",
            "category": "infrastructure_and_built_environment",
            "title": "Flood risk rising as sea levels increase",
            "summary": "PRD faces compound flood risk from typhoons and sea level rise; 40M people in high-risk coastal zones.",
            "sentiment": "negative",
            "strength": 0.78,
        },
    ],
    "economy_and_social_resilience": [
        {
            "id": "id_social_1",
            "category": "economy_and_social_resilience",
            "title": "GDP among top 10 regional economies globally",
            "summary": "Pearl River Delta GDP exceeds $2 trillion; home to Shenzhen's tech cluster, Guangzhou manufacturing, Macau tourism.",
            "sentiment": "positive",
            "strength": 0.88,
        },
        {
            "id": "id_social_2",
            "category": "economy_and_social_resilience",
            "title": "Migrant worker conditions and inequality",
            "summary": "The region's economic success depends on 30M+ internal migrants with limited social protections and high inequality.",
            "sentiment": "negative",
            "strength": 0.70,
        },
    ],
    "governance_and_policy": [
        {
            "id": "id_gov_1",
            "category": "governance_and_policy",
            "title": "Strong state capacity, selective enforcement",
            "summary": "Guangdong's government has capacity to implement large-scale policies but enforcement of environmental regulations is inconsistent.",
            "sentiment": "mixed",
            "strength": 0.65,
        },
        {
            "id": "id_gov_2",
            "category": "governance_and_policy",
            "title": "ETS carbon market operational since 2013",
            "summary": "Guangdong was among China's first regional ETS pilots; coverage expanding but carbon price remains below $15/tonne.",
            "sentiment": "mixed",
            "strength": 0.58,
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
