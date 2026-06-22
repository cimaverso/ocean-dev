from litestar import Controller, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from sqlalchemy.orm import Session
from dataclasses import dataclass

from src.core.db import get_db
from src.features.auth.schemas import (
    TokenResponse, RefreshTokenRequest,
    UsuarioCreate, UsuarioUpdate, UsuarioResponse,
)
from src.features.auth.services import UsuarioService
from src.core.security import crear_tokens, refrescar_token, guard_autenticado, guard_rol
from src.features.auth.services import usuario_autenticado


# Litestar no usa OAuth2PasswordRequestForm — recibimos usuario/clave en un schema simple
@dataclass
class LoginRequest:
    username: str
    password: str


class AuthController(Controller):
    path = "/autenticacion"
    tags = ["Autenticación"]
    dependencies = {"db": Provide(get_db)}

    @post("/ingresar", status_code=200)
    def iniciar_sesion(self, data: LoginRequest, db: Session) -> TokenResponse:
        usuario = usuario_autenticado(data.username, data.password, db)
        if not usuario:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        return crear_tokens(usuario.nombre, usuario.id, usuario.rol.nombre)

    @post("/refrescar", status_code=200)
    def renovar_token(self, data: RefreshTokenRequest) -> TokenResponse:
        return refrescar_token(data.refresh_token)


class UsuarioController(Controller):
    path = "/usuario"
    tags = ["Usuario"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_autenticado]  # todos los endpoints requieren token

    @get("/")
    def listar_usuarios(self, db: Session) -> list[UsuarioResponse]:
        return UsuarioService(db).listar_usuarios()

    @post("/", status_code=201, guards=[guard_rol(["ADMINISTRADOR"])])
    def crear_usuario(self, data: UsuarioCreate, db: Session) -> dict:
        nuevo = UsuarioService(db).crear_usuario(data)
        if not nuevo:
            raise HTTPException(status_code=400, detail="Error al crear el usuario")
        return {"message": "Usuario creado exitosamente."}

    @put("/{id:int}", guards=[guard_rol(["ADMINISTRADOR"])])
    def actualizar_usuario(self, id: int, data: UsuarioUpdate, db: Session) -> dict:
        actualizado = UsuarioService(db).actualizar_usuario(id, data)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"message": "Usuario actualizado exitosamente."}