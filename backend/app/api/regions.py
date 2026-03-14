"""REST endpoints for region data."""

from fastapi import APIRouter
from app.data.regions import list_regions, get_region

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("")
def get_regions():
    return {"regions": list_regions()}


@router.get("/{region_id}")
def get_region_detail(region_id: str):
    region = get_region(region_id)
    if not region:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Region not found")
    return region
