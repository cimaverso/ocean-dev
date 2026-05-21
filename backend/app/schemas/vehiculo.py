from pydantic import BaseModel
from typing import Optional

class VehiculoCreate(BaseModel):
    placa: str

class VehiculoUpdate(BaseModel):
    placa: Optional[str] = None

class VehiculoResponse(BaseModel):
    id: int
    placa: str

    model_config = {"from_attributes": True}