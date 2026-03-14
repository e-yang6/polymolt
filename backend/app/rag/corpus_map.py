"""
Corpus mapping — links agent category keys to named vector corpora.

In Phase 3 (current): provides constants and structure documentation.
In future RAG integration: corpora are populated by ingesting real documents
and queried by CategoryRetriever.

TODO: RAG — ingest documents into each corpus below using the pipeline in
      scripts/ingest.py (to be created). Then set RAG_ENABLED=true in config.
"""

from app.agents.agent_config import (
    CLIMATE, ENERGY, WATER, INFRA, SOCIAL, GOVERNANCE, ALL_CATEGORIES
)


# ─── Corpus name constants ─────────────────────────────────────────────────────
# In this system, corpus names ARE the category keys (snake_case).
# They are surfaced here for clarity and import convenience.

CORPUS_CLIMATE = CLIMATE              # "climate_and_emissions"
CORPUS_ENERGY = ENERGY                # "energy_and_resource_systems"
CORPUS_WATER = WATER                  # "water_and_ecosystems"
CORPUS_INFRA = INFRA                  # "infrastructure_and_built_environment"
CORPUS_SOCIAL = SOCIAL                # "economy_and_social_resilience"
CORPUS_GOVERNANCE = GOVERNANCE        # "governance_and_policy"

ALL_CORPORA: list[str] = ALL_CATEGORIES


# ─── Corpus → category mapping ─────────────────────────────────────────────────

CORPUS_TO_CATEGORY: dict[str, str] = {c: c for c in ALL_CORPORA}
CATEGORY_TO_CORPUS: dict[str, str] = {c: c for c in ALL_CORPORA}


def get_corpus_for_category(category: str) -> str:
    """Returns the corpus name for a given category key."""
    return CATEGORY_TO_CORPUS.get(category, category)


def get_category_for_corpus(corpus: str) -> str:
    """Returns the category key for a given corpus name."""
    return CORPUS_TO_CATEGORY.get(corpus, corpus)


# ─── Expected corpus file structure (for future ingestion) ─────────────────────
#
# TODO: RAG — create this directory structure and run scripts/ingest.py
#
# backend/
#   data/
#     corpora/
#       climate_and_emissions/
#         ipcc_ar6_summary.txt              # IPCC Sixth Assessment Report summary
#         national_emissions_2023.csv       # Country-level CO2 data
#         carbon_pricing_mechanisms.txt     # Carbon price survey
#         temperature_anomaly_data.csv      # NOAA/NASA anomaly records
#
#       energy_and_resource_systems/
#         iea_world_energy_outlook_2023.txt # IEA World Energy Outlook
#         renewable_capacity_irena.csv      # IRENA capacity statistics
#         resource_depletion_rates.txt      # Material flow accounts
#
#       water_and_ecosystems/
#         unep_water_stress_report.txt      # UNEP freshwater stress index
#         biodiversity_index_wwf.csv        # WWF Living Planet Index
#         deforestation_gfw_2023.csv        # Global Forest Watch data
#
#       infrastructure_and_built_environment/
#         urban_resilience_index.txt        # Arup urban resilience rankings
#         smart_city_benchmarks.csv         # ITU smart city KPIs
#         infrastructure_gap_report.txt     # McKinsey/ADB gap analysis
#
#       economy_and_social_resilience/
#         undp_hdi_2023.csv                 # UNDP Human Development Index
#         gini_world_bank.csv               # World Bank Gini coefficients
#         food_security_fao.txt             # FAO food security status
#
#       governance_and_policy/
#         esg_policy_index.csv              # BloombergNEF ESG policy scores
#         ndc_compliance_unfccc.txt         # UNFCCC NDC tracker
#         corruption_index_ti.csv           # Transparency International CPI
#
# Ingestion pipeline (to be built):
#   1. Chunk documents into ~512-token passages
#   2. Embed using config.EMBED_MODEL
#   3. Store in vector DB with metadata: {corpus, region_hint, doc_id}
#   4. CategoryRetriever queries by (embedding similarity + corpus filter)

CORPUS_DOC_HINTS: dict[str, list[str]] = {
    CORPUS_CLIMATE: [
        "IPCC assessment reports",
        "National emissions inventories",
        "Carbon pricing mechanisms",
        "Temperature and climate projections",
    ],
    CORPUS_ENERGY: [
        "IEA World Energy Outlook",
        "IRENA renewable capacity data",
        "Energy intensity metrics",
        "Grid decarbonization pathways",
    ],
    CORPUS_WATER: [
        "UNEP water stress indices",
        "Biodiversity and ecosystem health",
        "Deforestation rates (Global Forest Watch)",
        "Groundwater depletion data",
    ],
    CORPUS_INFRA: [
        "Urban resilience indices",
        "Smart city infrastructure benchmarks",
        "Infrastructure investment gap reports",
        "Green building standards",
    ],
    CORPUS_SOCIAL: [
        "UNDP Human Development Index",
        "World Bank Gini coefficients",
        "FAO food security reports",
        "Social protection coverage data",
    ],
    CORPUS_GOVERNANCE: [
        "Transparency International CPI",
        "UNFCCC NDC compliance tracker",
        "Environmental policy stringency indices",
        "ESG regulatory frameworks",
    ],
}
