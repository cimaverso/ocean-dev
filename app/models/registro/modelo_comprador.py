from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .modelo_registro import Registro  # Importar aquí para evitar problemas de referencia circular

# Modelo de Base de Datos (Tabla)
class Comprador(SQLModel, table=True):
    __tablename__ = "comprador"
    comp_id: int = Field(primary_key=True, index=True)
    comp_nombre: str
    comp_nit: Optional[str] = None
    comp_telefono: Optional[str] = None
    comp_codigo: Optional[str] = None

    registros: list['Registro'] = Relationship(back_populates="comprador")


# Esquema para Crear
class CompradorCreate(SQLModel):
    comp_nombre: str
    comp_nit: Optional[str] = None
    comp_telefono: Optional[str] = None
    comp_codigo: Optional[str] = None


# Esquema para Actualizar
class CompradorUpdate(SQLModel):
    comp_nombre: Optional[str] = None
    comp_nit: Optional[str] = None
    comp_telefono: Optional[str] = None
    comp_codigo: Optional[str] = None


# Esquema para Respuesta
class CompradorResponse(SQLModel):
    comp_id: int
    comp_nombre: str
    comp_nit: Optional[str] = None
    comp_telefono: Optional[str] = None
    comp_codigo: Optional[str] = None

    model_config = {"from_attributes": True}

