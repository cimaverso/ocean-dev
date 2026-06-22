from pydantic import BaseModel
from typing import Optional


class ConductorCreate(BaseModel):
    nombre: str
    cedula: Optional[str] = None
    telefono: Optional[str] = None


class ConductorUpdate(BaseModel):
    nombre: Optional[str] = None
    cedula: Optional[str] = None
    telefono: Optional[str] = None


class ConductorResponse(BaseModel):
    id: int
    nombre: str
    cedula: Optional[str] = None
    telefono: Optional[str] = None

    model_config = {"from_attributes": True}