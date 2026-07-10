from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_metrics():
    return {"message": "Metrics endpoint - under construction"}