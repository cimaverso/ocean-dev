from pydantic import BaseModel

class RolCreate(BaseModel):
    nombre: str

class RolResponse(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}