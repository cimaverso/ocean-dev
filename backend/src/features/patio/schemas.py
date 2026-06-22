from pydantic import BaseModel
from typing import Optional


class PatioCreate(BaseModel):
    nombre: str
    codigo: Optional[str] = None


class PatioUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None


class PatioResponse(BaseModel):
    id: int
    nombre: str
    codigo: Optional[str] = None

    model_config = {"from_attributes": True}