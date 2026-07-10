from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def export_data():
    return {"message": "Export endpoint - under construction"}