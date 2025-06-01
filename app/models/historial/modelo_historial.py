from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import date, time
from app.models.usuario.modelo_usuario import UsuarioResponse
from app.models.registro.modelo_registro import RegistroResponse


if TYPE_CHECKING:
    from app.models.usuario.modelo_usuario import Usuario
    from app.models.registro.modelo_registro import Registro

class Historial(SQLModel, table=True):
    __tablename__ = "historial"
    his_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    his_accion: str
    his_fecha: date 
    his_hora: time
    his_idusuario: int = Field(foreign_key="usuario.usuario_id")
    his_idregistro: int = Field(foreign_key="registro.reg_id")


    usuario: 'Usuario' = Relationship(back_populates="historial")
    registro: 'Registro' = Relationship(back_populates="historial")

class HistorialResponse(SQLModel):
    his_id: int
    his_accion: str
    his_fecha: date
    his_hora: time
    usuario: UsuarioResponse
    registro: RegistroResponse

    model_config = {"from_attributes": True}