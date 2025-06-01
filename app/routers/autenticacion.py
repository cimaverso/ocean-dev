from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from app.core.core_auth import usuario_autenticado, crear_tokens, refrescar_token
from app.models.modelo_auth import TokenResponse, RefreshTokenResponse
from app.config.database import get_db


router = APIRouter(
    prefix='/autenticacion',
    tags=['Autenticación']
)

@router.post("/ingresar", include_in_schema=False, response_model=TokenResponse)
def iniciar_sesion(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = usuario_autenticado(form_data.username, form_data.password, db)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    return crear_tokens(usuario.usuario_nombre, usuario.usuario_id, usuario.rol.rol_nombre)

@router.post("/refrescar", include_in_schema=False, response_model=TokenResponse)
def renovar_token(data: RefreshTokenResponse):
    return refrescar_token(data.refresh_token)




