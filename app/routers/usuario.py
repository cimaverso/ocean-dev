from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.usuario.modelo_usuario import UsuarioResponse, UsuarioCreate, UsuarioUpdate
from app.services.servicio_usuario import UsuarioService
from app.config.database import get_db
from app.core.core_auth import verificar_rol

router = APIRouter(
    prefix='/usuario',
    tags=['Usuario']
)

@router.get('/', response_model=list[UsuarioResponse], status_code=status.HTTP_200_OK)
def listar_usuarios(db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    usuario_service = UsuarioService(db)
    usuarios = usuario_service.listar_usuarios()
    return usuarios

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario_data: UsuarioCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    
    usuario_service = UsuarioService(db)
    nuevo_usuario = usuario_service.crear_usuario(usuario_data)

    if not nuevo_usuario:
        raise HTTPException(status_code=400, detail="Error al crear el usuario")
    return {"message": "Usuario creado exitosamente."}
        
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_usuario(id: int, usuario_data: UsuarioUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
   
    usuario_service = UsuarioService(db)
    usuario_actualizado = usuario_service.actualizar_usuario(id, usuario_data)

    if not usuario_actualizado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"message": "Usuario actualizado exitosamente."}
    
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    usuario_service = UsuarioService(db)
    eliminado = usuario_service.eliminar_usuario(id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {"message": "Usuario eliminado exitosamente."}

