from pydantic import BaseModel
from typing import Optional

class UnidadMedidaCreate(BaseModel):
    nombre: str

class UnidadMedidaUpdate(BaseModel):
    nombre: Optional[str] = None

class UnidadMedidaResponse(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}