from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .modelo_usuario import Usuario  # Importar aquí para evitar problemas de referencia circular



class Rol(SQLModel, table=True):
    __tablename__ = "rol"
    rol_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    rol_nombre: str

    usuario: list["Usuario"] = Relationship(back_populates="rol")


class RolCreate(SQLModel):
    rol_nombre: str
   

class RolResponse(SQLModel):
    rol_id: int
    rol_nombre: str

    model_config = {"from_attributes": True}
    

    