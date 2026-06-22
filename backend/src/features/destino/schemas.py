from pydantic import BaseModel
from typing import Optional


class DestinoCreate(BaseModel):
    nombre: str
    codigo: Optional[str] = None


class DestinoUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None


class DestinoResponse(BaseModel):
    id: int
    nombre: str
    codigo: Optional[str] = None

    model_config = {"from_attributes": True}