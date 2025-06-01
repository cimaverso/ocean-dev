from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .modelo_registro import Registro  # Importar aquí para evitar problemas de referencia circular


class Transportadora(SQLModel, table=True):
    __tablename__ = "transportadora"
    trans_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    trans_nombre: str
    trans_ciudad: Optional[str] = None
    trans_direccion: Optional[str] = None
    trans_nit: Optional[str] = None
    trans_telefono: Optional[str] = None
    trans_codigo: Optional[str] = None

    registros: list["Registro"] = Relationship(back_populates="transportadora")

class TransportadoraCreate(SQLModel):
    trans_nombre: str
    trans_ciudad: Optional[str] = None
    trans_direccion: Optional[str] = None
    trans_nit: Optional[str] = None
    trans_telefono: Optional[str] = None
    trans_codigo: Optional[str] = None

class TransportadoraUpdate(SQLModel):
    trans_nombre: Optional[str] = None
    trans_ciudad: Optional[str] = None
    trans_direccion: Optional[str] = None
    trans_nit: Optional[str] = None
    trans_telefono: Optional[str] = None
    trans_codigo: Optional[str] = None

class TransportadoraResponse(SQLModel):
    trans_id: int
    trans_nombre: str
    trans_ciudad: Optional[str] = None
    trans_direccion: Optional[str] = None
    trans_nit: Optional[str] = None
    trans_telefono: Optional[str] = None
    trans_codigo: Optional[str] = None

    model_config = {"from_attributes": True}

