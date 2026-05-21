from pydantic import BaseModel
from typing import Optional

class TrailerCreate(BaseModel):
    placa: str

class TrailerUpdate(BaseModel):
    placa: Optional[str] = None

class TrailerResponse(BaseModel):
    id: int
    placa: str

    model_config = {"from_attributes": True}