from pydantic import BaseModel
from datetime import date, time
from src.features.auth.schemas import UsuarioResponse
from src.features.registro.schemas import RegistroResponse


class HistorialResponse(BaseModel):
    id: int
    accion: str
    fecha: date
    hora: time
    usuario: UsuarioResponse
    registro: RegistroResponse

    model_config = {"from_attributes": True}