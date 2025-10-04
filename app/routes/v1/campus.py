from fastapi import APIRouter

from app.schema.campus import CreateCampusModel
from app.services.campus import list_campuses, create_campus


router = APIRouter()


@router.get("/")
async def campus():
    return await list_campuses()

@router.post("/")
async def create(payload: CreateCampusModel):
    return await create_campus(payload)