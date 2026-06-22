from pydantic import BaseModel
from typing import Optional


class OrigenCreate(BaseModel):
    nombre: str
    codigo: Optional[str] = None


class OrigenUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None


class OrigenResponse(BaseModel):
    id: int
    nombre: str
    codigo: Optional[str] = None

    model_config = {"from_attributes": True}