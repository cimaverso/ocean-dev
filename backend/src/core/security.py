from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from litestar.exceptions import HTTPException
from litestar.connection import ASGIConnection
from litestar.handlers import BaseRouteHandler
from typing import Dict, Any


from src.core.config import settings

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Password ---

def verificar_password(clave_plana: str, clave_hash: str) -> bool:
    return bcrypt_context.verify(clave_plana, clave_hash)

def hash_password(clave: str) -> str:
    return bcrypt_context.hash(clave)

# --- Tokens ---

def crear_token(
    usuario_nombre: str,
    usuario_id: int,
    rol_nombre: str,
    expires_delta: timedelta,
    token_type: str = "access",
) -> str:
    data = {
        "sub": usuario_nombre,
        "id": usuario_id,
        "role": rol_nombre,
        "type": token_type,
        "exp": datetime.utcnow() + expires_delta,
    }
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def crear_tokens(usuario_nombre: str, usuario_id: int, rol_nombre: str) -> Dict[str, Any]:
    access_token = crear_token(
        usuario_nombre, usuario_id, rol_nombre,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), "access"
    )
    refresh_token = crear_token(
        usuario_nombre, usuario_id, rol_nombre,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "refresh"
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "username": usuario_nombre,
        "user_id": usuario_id,
        "role": rol_nombre,
    }


def refrescar_token(refresh_token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token no válido para refrescar")
        return crear_tokens(payload["sub"], payload["id"], payload["role"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")


# --- Guards (reemplazan Depends(obtener_usuario) y Depends(verificar_rol)) ---

def obtener_payload(connection: ASGIConnection) -> Dict[str, Any]:
    """Extrae y valida el token Bearer del header Authorization."""
    auth_header = connection.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Token no válido para acceso")
        return {
            "usuario_nombre": payload["sub"],
            "usuario_id": payload["id"],
            "usuario_rol": payload["role"],
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


def guard_autenticado(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard: solo requiere estar autenticado."""
    obtener_payload(connection)


def guard_rol(roles_permitidos: list[str]):
    """Guard factory: requiere uno de los roles dados."""
    def _guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
        usuario = obtener_payload(connection)
        if usuario["usuario_rol"] not in roles_permitidos:
            raise HTTPException(status_code=403, detail="No tienes permisos suficientes")
    return _guard