from pydantic import BaseModel
from typing import Optional

class CompradorCreate(BaseModel):
    nombre: str
    nit: Optional[str] = None
    telefono: Optional[str] = None
    codigo: Optional[str] = None

class CompradorUpdate(BaseModel):
    nombre: Optional[str] = None
    nit: Optional[str] = None
    telefono: Optional[str] = None
    codigo: Optional[str] = None

class CompradorResponse(BaseModel):
    id: int
    nombre: str
    nit: Optional[str] = None
    telefono: Optional[str] = None
    codigo: Optional[str] = None

    model_config = {"from_attributes": True}