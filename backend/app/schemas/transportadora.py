from pydantic import BaseModel
from typing import Optional

class TransportadoraCreate(BaseModel):
    nombre: str
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    nit: Optional[str] = None
    telefono: Optional[str] = None
    codigo: Optional[str] = None

class TransportadoraUpdate(BaseModel):
    nombre: Optional[str] = None
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    nit: Optional[str] = None
    telefono: Optional[str] = None
    codigo: Optional[str] = None

class TransportadoraResponse(BaseModel):
    id: int
    nombre: str
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    nit: Optional[str] = None
    telefono: Optional[str] = None
    codigo: Optional[str] = None

    model_config = {"from_attributes": True}