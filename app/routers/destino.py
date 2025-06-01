# routers/destino.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.registro.modelo_destino import DestinoResponse, DestinoCreate, DestinoUpdate
from app.services.servicio_destino import DestinoService
from app.config.database import get_db
from app.core.core_auth import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional


router = APIRouter(
    prefix='/destino',
    tags=['Destino']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_destinos(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    destino_service = DestinoService(db)
    output = destino_service.exportar_destinos(consulta)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=destinos.xlsx"})

# Listar destinos
@router.get('/', response_model=list[DestinoResponse], status_code=status.HTTP_200_OK)
def obtener_destinos(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    destino_service = DestinoService(db)
    destinos = destino_service.listar_destinos()
    return destinos

# Crear destino
@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_destino(destino: DestinoCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    destino_service = DestinoService(db)
    nuevo_destino = destino_service.crear_destino(destino)
    if not nuevo_destino:
        raise HTTPException(status_code=400, detail="Error al crear el destino")
    
    return {"message": "Destino creado exitosamente."}

# Actualizar destino
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_destino(id: int, destino: DestinoUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    destino_service = DestinoService(db)
    destino_actualizado = destino_service.actualizar_destino(id, destino)

    if not destino_actualizado:
        raise HTTPException(status_code=404, detail="Destino no encontrado")

    return {"message": "Destino actualziado exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_destino(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    destino_service = DestinoService(db)
    eliminado = destino_service.eliminar_destino(id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Destino no encontrado")

    return {"message": "Destino eliminado exitosamente."}

