from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def start_training():
    return {"message": "Training endpoint - under construction"}