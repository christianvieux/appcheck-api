from fastapi import APIRouter, FastAPI

router = APIRouter()


@router.get("/ping", status_code=200) # better than "/health" :P
async def read_ping():
    return {"message": "Pong!"}