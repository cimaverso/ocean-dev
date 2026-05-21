from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.transportadora import TransportadoraResponse, TransportadoraCreate, TransportadoraUpdate
from app.services.transportadora import TransportadoraService
from app.config.database import get_db
from app.core.security import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/transportadora',
    tags=['Transportadora']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_transportadoras(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    output = TransportadoraService(db).exportar_transportadoras(consulta)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail="No hay datos para exportar")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=transportadoras.xlsx"})

@router.get('/', response_model=list[TransportadoraResponse], status_code=status.HTTP_200_OK)
def obtener_transportadoras(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return TransportadoraService(db).obtener_transportadoras()

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_transportadora(transportadora: TransportadoraCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    nueva = TransportadoraService(db).crear_transportadora(transportadora)
    if not nueva:
        raise HTTPException(status_code=400, detail="Error al crear la transportadora")
    return {"message": "Transportadora creada exitosamente."}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_transportadora(id: int, transportadora: TransportadoraUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    actualizada = TransportadoraService(db).actualizar_transportadora(id, transportadora)
    if not actualizada:
        raise HTTPException(status_code=404, detail="Transportadora no encontrada")
    return {"message": "Transportadora actualizada exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_transportadora(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    if not TransportadoraService(db).eliminar_transportadora(id):
        raise HTTPException(status_code=404, detail="Transportadora no encontrada")