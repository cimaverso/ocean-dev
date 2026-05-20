from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .modelo_registro import Registro  # Importar aquí para evitar problemas de referencia circular


class Origen(SQLModel, table=True):
    __tablename__ = "origen"
    ori_id: int = Field(primary_key=True, index=True, alias="origen_id")
    ori_nombre: str 
    ori_codigo: Optional[str] = None

    registros: list["Registro"] = Relationship(back_populates="origen")

class OrigenCreate(SQLModel):
    ori_nombre: str
    ori_codigo: Optional[str] = None

class OrigenUpdate(SQLModel):
    ori_nombre: Optional[str] = None
    ori_codigo: Optional[str] = None
  

class OrigenResponse(SQLModel):
    ori_id: int
    ori_nombre: str
    ori_codigo: Optional[str] = None

    model_config = {"from_attributes": True}

