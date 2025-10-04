

from app.models.index import Campus
from app.schema.campus import CreateCampusModel
from fastapi.exceptions import HTTPException
from tortoise.exceptions import IntegrityError


async def list_campuses():
    return await Campus.all()

async def create_campus(payload: CreateCampusModel):
    try:
        campus = await Campus.create(
            name=payload.name
        )
    except IntegrityError:
        raise HTTPException(detail="Campus with the provided name already exists", status_code=400)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return campus


