from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .modelo_registro import Registro  # Importar aquí para evitar problemas de referencia circular    

class Trailer(SQLModel, table=True):
    __tablename__ = "trailer"
    trai_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    trai_placa: str

    registros: list["Registro"] = Relationship(back_populates="trailer")

class TrailerCreate(SQLModel):
    trai_placa: str

class TrailerUpdate(SQLModel):
    trai_placa: Optional[str] = None

class TrailerResponse(SQLModel):
    trai_id: int
    trai_placa: str
    
    model_config = {"from_attributes": True}
