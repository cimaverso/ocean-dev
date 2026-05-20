from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.registro.modelo_trailer import TrailerResponse, TrailerCreate, TrailerUpdate
from app.services.servicio_trailer import TrailerService
from app.config.database import get_db
from fastapi.responses import StreamingResponse
from typing import Optional
from app.core.core_auth import obtener_usuario, verificar_rol

router = APIRouter(
    prefix='/trailer',
    tags=['Trailer']
)



@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_trailers(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    trailer_service = TrailerService(db)
    output = trailer_service.exportar_trailers(consulta)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=trailers.xlsx"})

# Listar trailers
@router.get('/',  response_model=list[TrailerResponse], status_code=status.HTTP_200_OK)
def obtener_trailers(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    trailer_service = TrailerService(db)
    trailers = trailer_service.listar_trailers()
    return trailers

# Crear trailer
@router.post('/', response_model=TrailerResponse, status_code=status.HTTP_201_CREATED)
def crear_trailer(trailer: TrailerCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    trailer_service = TrailerService(db)
    nuevo_trailer = trailer_service.crear_trailer(trailer)
    if not nuevo_trailer:
        raise HTTPException(status_code=400, detail="Error al crear el trailer")

    return nuevo_trailer

# Actualizar trailer
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_trailer(id: int, trailer: TrailerUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    trailer_service = TrailerService(db)
    trailer_actualizado = trailer_service.actualizar_trailer(id, trailer)

    if not trailer_actualizado:
        raise HTTPException(status_code=404, detail="Trailer no encontrado")

    return {"message": "Trailer actualizado exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_trailer(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    trailer_service = TrailerService(db)
    eliminado = trailer_service.eliminar_trailer(id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Trailer no encontrado")

    return {"message": "Trailer eliminado exitosamente."}
