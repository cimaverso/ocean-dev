from pydantic import BaseModel
from typing import Optional


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    username: str
    user_id: int
    role: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UsuarioCreate(BaseModel):
    nombre: str
    correo: Optional[str] = None
    clave: str
    rol_id: int


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[str] = None
    clave: Optional[str] = None
    rol_id: Optional[int] = None


class RolResponse(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    correo: Optional[str] = None
    rol: RolResponse

    model_config = {"from_attributes": True}