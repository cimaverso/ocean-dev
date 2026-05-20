from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship



if TYPE_CHECKING:
    from .modelo_registro import Registro  # Importar aquí para evitar problemas de referencia circular


class Destino(SQLModel, table=True):
    __tablename__ = "destino"
    dest_id: int = Field(primary_key=True, index=True)
    dest_nombre: str 
    dest_codigo: Optional[str] = None

    registros: list["Registro"] = Relationship(back_populates="destino")

class DestinoCreate(SQLModel):
    dest_nombre: str 
    dest_codigo: Optional[str] = None

class DestinoUpdate(SQLModel):
    dest_nombre: Optional[str] = None
    dest_codigo: Optional[str] = None
 
class DestinoResponse(SQLModel):
    dest_id: int 
    dest_nombre: str 
    dest_codigo: Optional[str] = None

    model_config = {"from_attributes": True}

    





