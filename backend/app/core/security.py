from fastapi import Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.orm import selectinload
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from app.models.usuario.modelo_usuario import Usuario
from app.core.config import settings
from typing import Dict, Optional, Union

# Contexto para encriptación de contraseñas
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="autenticacion/ingresar")

def crear_token(usuario_nombre: str, usuario_id: int, rol_nombre: str, expires_delta: timedelta, token_type: str = "access") -> str:
    data = {
        "sub": usuario_nombre,
        "id": usuario_id,
        "role": rol_nombre,
        "type": token_type,
        "exp": datetime.utcnow() + expires_delta
    }
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def crear_tokens(usuario_nombre: str, usuario_id: int, rol_nombre: str) -> Dict[str, str]:
    access_token = crear_token(
        usuario_nombre, usuario_id, rol_nombre,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), 'access'
    )
    refresh_token = crear_token(
        usuario_nombre, usuario_id, rol_nombre,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), 'refresh'
    )
    return {
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "token_type":    "bearer",
        "username":      usuario_nombre,
        "user_id":       usuario_id,
        "role":          rol_nombre,
    }

def verificar_password(clave_plana: str, clave_hash: str) -> bool:
    return bcrypt_context.verify(clave_plana, clave_hash)

def hash_password(clave: str) -> str:
    return bcrypt_context.hash(clave)

def refrescar_token(refresh_token: str) -> Dict[str, str]:
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token no válido para refrescar"
            )
        return crear_tokens(payload["sub"], payload["id"], payload["role"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado"
        )

def usuario_autenticado(usuario_nombre: str, usuario_clave: str, db) -> Optional[Usuario]:
    statement = select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.usuario_nombre == usuario_nombre)
    usuario = db.exec(statement).first()
    if not usuario or not verificar_password(usuario_clave, usuario.usuario_clave):
        return None
    return usuario

async def obtener_usuario(token: str = Depends(oauth2_bearer)) -> Dict[str, Union[str, int]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token no válido para acceso"
            )
        return {
            "usuario_nombre": payload["sub"],
            "usuario_id": payload["id"],
            "usuario_rol": payload["role"]
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

def verificar_rol(roles_permitidos: list[str]):
    async def verificar_rol_auth(usuario: dict = Depends(obtener_usuario)):
        if usuario["usuario_rol"] not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para esta acción"
            )
        return usuario
    return verificar_rol_auth
