from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def retrain_model():
    return {"message": "Retrain endpoint - under construction"}