"""
Seeded demo regions for Polymolt.
Three regions with distinct sustainability profiles for demo purposes.
"""

from typing import TypedDict


class RegionInfo(TypedDict):
    id: str
    name: str
    description: str
    profile: str  # "sustainable" | "weak" | "contested"
    lmsr_b: float  # liquidity parameter — higher = slower market


REGIONS: dict[str, RegionInfo] = {
    "scandinavia": {
        "id": "scandinavia",
        "name": "Scandinavia (Nordic Model)",
        "description": (
            "Denmark, Sweden, Norway, and Finland — among the world's highest performers "
            "on renewable energy, social welfare, governance quality, and environmental policy. "
            "Some tensions between offshore oil wealth (Norway) and decarbonization goals."
        ),
        "profile": "sustainable",
        "lmsr_b": 60.0,
    },
    "drought_belt": {
        "id": "drought_belt",
        "name": "Sub-Saharan Drought Belt",
        "description": (
            "A composite of drought-stressed sub-Saharan regions including the Sahel and "
            "parts of East Africa. Characterized by severe water stress, fragile governance, "
            "low renewable energy penetration, and high climate vulnerability."
        ),
        "profile": "weak",
        "lmsr_b": 50.0,
    },
    "industrial_delta": {
        "id": "industrial_delta",
        "name": "Industrial Delta (Pearl River)",
        "description": (
            "The Pearl River Delta in southern China — one of the world's largest manufacturing "
            "and export hubs. Strong economic growth and infrastructure, but severe air and water "
            "pollution, ecosystem degradation, and governance challenges around enforcement."
        ),
        "profile": "contested",
        "lmsr_b": 45.0,
    },
}


def get_region(region_id: str) -> RegionInfo | None:
    return REGIONS.get(region_id)


def list_regions() -> list[RegionInfo]:
    return list(REGIONS.values())
