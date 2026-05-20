from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .modelo_registro import Registro # Importar aquí para evitar problemas de referencia circular


class Conductor(SQLModel, table=True):
    __tablename__ = "conductor"
    conduct_id: int = Field(primary_key=True, index=True)
    conduct_nombre: str 
    conduct_cedula: Optional[str] = None
    conduct_telefono: Optional[str] = None
    

    registros: list['Registro'] = Relationship(back_populates="conductor")

class ConductorCreate(SQLModel):
    conduct_nombre: str
    conduct_cedula: Optional[str] = None
    conduct_telefono: Optional[str] = None
    

class ConductorUpdate(SQLModel):
    conduct_nombre: Optional[str] = None
    conduct_cedula: Optional[str] = None
    conduct_telefono: Optional[str] = None
    


class ConductorResponse(SQLModel):
    conduct_id: int
    conduct_nombre: str 
    conduct_cedula: Optional[str] = None
    conduct_telefono: Optional[str] = None
   

    model_config = {"from_attributes": True}
        

