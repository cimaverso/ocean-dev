from pydantic import BaseModel
from typing import Optional
from app.schemas.tipo_entidad import TipoEntidadResponse

class EntidadCreate(BaseModel):
    tipo_id: int
    nombre: str
    nit: Optional[str] = None
    telefono: Optional[str] = None
    codigo: Optional[str] = None

class EntidadUpdate(BaseModel):
    tipo_id: Optional[int] = None
    nombre: Optional[str] = None
    nit: Optional[str] = None
    telefono: Optional[str] = None
    codigo: Optional[str] = None

class EntidadResponse(BaseModel):
    id: int
    nombre: str
    tipo: TipoEntidadResponse
    nit: Optional[str] = None
    telefono: Optional[str] = None
    codigo: Optional[str] = None

    model_config = {"from_attributes": True}