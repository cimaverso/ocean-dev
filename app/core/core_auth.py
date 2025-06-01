from fastapi import Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.orm import selectinload
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from app.models.usuario.modelo_usuario import Usuario
import os
from dotenv import load_dotenv
from typing import Dict, Optional, Union

load_dotenv()

# Constantes de configuración
SECRET_KEY = os.getenv("SECRET_KEY", "dcb70deed293f60179c36c76d3a8699cc0c4940a7758729a5f011dd0143f23d6")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

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
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def crear_tokens(usuario_nombre: str, usuario_id: int, rol_nombre: str) -> Dict[str, str]:
 
    access_token = crear_token(
        usuario_nombre, 
        usuario_id, 
        rol_nombre, 
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), 
        'access'
    )
    refresh_token = crear_token(
        usuario_nombre, 
        usuario_id, 
        rol_nombre, 
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), 
        'refresh'
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

def verificar_password(clave_plana: str, clave_hash: str) -> bool:
    #Verifica si la contraseña es correcta
    return bcrypt_context.verify(clave_plana, clave_hash)

def hash_password(clave: str) -> str:
    #Genera el hash de la contraseña
    return bcrypt_context.hash(clave)

def refrescar_token(refresh_token: str) -> Dict[str, str]:

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verificar que sea un token de refresco
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
    #Verificar si el usuario esta autenticado
    statement = select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.usuario_nombre == usuario_nombre)
    usuario = db.exec(statement).first()
    
    if not usuario or not verificar_password(usuario_clave, usuario.usuario_clave):
        return None
    return usuario

async def obtener_usuario(token: str = Depends(oauth2_bearer)) -> Dict[str, Union[str, int]]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verificar que sea un token de acceso
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