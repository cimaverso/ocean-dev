from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.usuario import UsuarioResponse, UsuarioCreate, UsuarioUpdate
from app.services.usuario import UsuarioService
from app.config.database import get_db
from app.core.security import verificar_rol

router = APIRouter(
    prefix='/usuario',
    tags=['Usuario']
)

@router.get('/', response_model=list[UsuarioResponse], status_code=status.HTTP_200_OK)
def listar_usuarios(db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    return UsuarioService(db).listar_usuarios()

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario_data: UsuarioCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    nuevo = UsuarioService(db).crear_usuario(usuario_data)
    if not nuevo:
        raise HTTPException(status_code=400, detail="Error al crear el usuario")
    return {"message": "Usuario creado exitosamente."}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_usuario(id: int, usuario_data: UsuarioUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    actualizado = UsuarioService(db).actualizar_usuario(id, usuario_data)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario actualizado exitosamente."}

