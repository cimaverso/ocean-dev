from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.registro.entidad.modelo_tipoentidad import TipoEntidadResponse


if TYPE_CHECKING:
    from app.models.registro.modelo_registro import Registro  # Importar aquí para evitar problemas de referencia circular
    from .modelo_tipoentidad import TipoEntidad  # Importar aquí para evitar problemas de referencia circular



class Entidad(SQLModel, table=True):
    __tablename__ = "entidad"
    ent_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    ent_idtipoentidad: int = Field(foreign_key="tipo_entidad.tpent_id")
    ent_nombre: str
    ent_nit: Optional[str] = None
    ent_telefono: Optional[str] = None
    ent_codigo: Optional[str] = None

    tipo: 'TipoEntidad' = Relationship(back_populates="entidad")
    registros: list["Registro"] = Relationship(back_populates="entidad")

class EntidadCreate(SQLModel):
    ent_idtipoentidad: int
    ent_nombre: str
    ent_nit: Optional[str] = None
    ent_telefono: Optional[str] = None
    ent_codigo: Optional[str] = None

class EntidadUpdate(SQLModel):
    ent_idtipoentidad: Optional[int] = None
    ent_nombre: Optional[str] = None
    ent_nit: Optional[str] = None
    ent_telefono: Optional[str] = None
    ent_codigo: Optional[str] = None
   

class EntidadResponse(SQLModel):
    ent_id: int
    ent_nombre: str
    tipo: TipoEntidadResponse
    ent_nit: Optional[str] = None
    ent_telefono: Optional[str] = None
    ent_codigo: Optional[str] = None
  

    model_config = {"from_attributes": True}



