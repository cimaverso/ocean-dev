from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.destino import DestinoResponse, DestinoCreate, DestinoUpdate
from app.services.destino import DestinoService
from app.config.database import get_db
from app.core.security import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/destino',
    tags=['Destino']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_destinos(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    output = DestinoService(db).exportar_destinos(consulta)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail="No hay datos para exportar")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=destinos.xlsx"})

@router.get('/', response_model=list[DestinoResponse], status_code=status.HTTP_200_OK)
def obtener_destinos(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return DestinoService(db).listar_destinos()

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_destino(destino: DestinoCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    nuevo = DestinoService(db).crear_destino(destino)
    if not nuevo:
        raise HTTPException(status_code=400, detail="Error al crear el destino")
    return {"message": "Destino creado exitosamente."}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_destino(id: int, destino: DestinoUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    actualizado = DestinoService(db).actualizar_destino(id, destino)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Destino no encontrado")
    return {"message": "Destino actualizado exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_destino(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    if not DestinoService(db).eliminar_destino(id):
        raise HTTPException(status_code=404, detail="Destino no encontrado")