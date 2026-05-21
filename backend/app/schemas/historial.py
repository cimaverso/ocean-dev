from pydantic import BaseModel
from datetime import date, time
from app.schemas.usuario import UsuarioResponse
from app.schemas.registro import RegistroResponse

class HistorialResponse(BaseModel):
    id: int
    accion: str
    fecha: date
    hora: time
    usuario: UsuarioResponse
    registro: RegistroResponse

    model_config = {"from_attributes": True}