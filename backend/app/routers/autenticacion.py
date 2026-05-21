from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import usuario_autenticado, crear_tokens, refrescar_token
from app.schemas.auth import TokenResponse, RefreshTokenResponse
from app.config.database import get_db

router = APIRouter(
    prefix='/autenticacion',
    tags=['Autenticación']
)

@router.post("/ingresar", response_model=TokenResponse)
def iniciar_sesion(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = usuario_autenticado(form_data.username, form_data.password, db)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return crear_tokens(usuario.nombre, usuario.id, usuario.rol.nombre)

@router.post("/refrescar", response_model=TokenResponse)
def renovar_token(data: RefreshTokenResponse):
    return refrescar_token(data.refresh_token)