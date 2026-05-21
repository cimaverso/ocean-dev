from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.trailer import TrailerResponse, TrailerCreate, TrailerUpdate
from app.services.trailer import TrailerService
from app.config.database import get_db
from app.core.security import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/trailer',
    tags=['Trailer']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_trailers(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    output = TrailerService(db).exportar_trailers(consulta)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail="No hay datos para exportar")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=trailers.xlsx"})

@router.get('/', response_model=list[TrailerResponse], status_code=status.HTTP_200_OK)
def obtener_trailers(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return TrailerService(db).obtener_trailers()

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_trailer(trailer: TrailerCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    nuevo = TrailerService(db).crear_trailer(trailer)
    if not nuevo:
        raise HTTPException(status_code=400, detail="Error al crear el trailer")
    return {"message": "Trailer creado exitosamente."}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_trailer(id: int, trailer: TrailerUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    actualizado = TrailerService(db).actualizar_trailer(id, trailer)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Trailer no encontrado")
    return {"message": "Trailer actualizado exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_trailer(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    if not TrailerService(db).eliminar_trailer(id):
        raise HTTPException(status_code=404, detail="Trailer no encontrado")