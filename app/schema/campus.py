from pydantic import BaseModel

class CreateCampusModel(BaseModel):
    name: str