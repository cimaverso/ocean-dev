from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .modelo_registro import Registro  # Importar aquí para evitar problemas de referencia circular


class Patio(SQLModel, table=True):
    __tablename__ = "patio"
    pat_id: int = Field(primary_key=True, index=True)
    pat_nombre: str 
    pat_codigo: Optional[str] = None

    registros: list["Registro"] = Relationship(back_populates="patio")

class PatioCreate(SQLModel):
    pat_nombre: str
    pat_codigo: Optional[str] = None

class PatioUpdate(SQLModel):
    pat_nombre: Optional[str] = None
    pat_codigo: Optional[str] = None


class PatioResponse(SQLModel):
    pat_id: int
    pat_nombre: str
    pat_codigo: Optional[str] = None

    model_config = {"from_attributes": True}

