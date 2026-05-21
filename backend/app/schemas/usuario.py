from pydantic import BaseModel
from typing import Optional
from app.schemas.rol import RolResponse

class UsuarioCreate(BaseModel):
    nombre: str
    clave: str
    correo: Optional[str] = None
    rol_id: int

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[str] = None
    clave: Optional[str] = None
    rol_id: Optional[int] = None

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    correo: Optional[str] = None
    rol: RolResponse

    model_config = {"from_attributes": True}