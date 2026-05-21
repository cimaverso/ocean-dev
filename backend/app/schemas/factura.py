from pydantic import BaseModel
from typing import Optional

class FacturaCreate(BaseModel):
    fecha: str

class FacturaUpdate(BaseModel):
    fecha: Optional[str] = None

class FacturaResponse(BaseModel):
    id: int
    fecha: str

    model_config = {"from_attributes": True}