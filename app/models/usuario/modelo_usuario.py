from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from app.models.usuario.modelo_rol import RolResponse


if TYPE_CHECKING:
    from .modelo_rol import Rol  # Importar aquí para evitar problemas de referencia circular
    from app.models.historial.modelo_historial import Historial



class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"
    usuario_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    usuario_nombre: str
    usuario_correo: Optional[str] = None
    usuario_clave: str
    usuario_idrol: int = Field(default=None, foreign_key="rol.rol_id")
    

    rol: 'Rol' = Relationship(back_populates="usuario")
    historial: List['Historial'] = Relationship(back_populates="usuario")

class UsuarioCreate(SQLModel):
    usuario_nombre: str
    usuario_clave: str
    usuario_correo: Optional[str] = None
    usuario_idrol: int
    
class UsuarioUpdate(SQLModel):
    usuario_nombre: Optional[str] = None
    usuario_correo: Optional[str] = None
    usuario_clave: Optional[str] = None
    usuario_idrol: Optional[int] = None 

class UsuarioResponse(SQLModel):
    usuario_id: int
    usuario_nombre: str
    usuario_correo: Optional[str] = None
    rol: RolResponse

    model_config = {"from_attributes": True}

