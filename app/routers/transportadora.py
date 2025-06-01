from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.registro.modelo_transportadora import TransportadoraResponse, TransportadoraCreate, TransportadoraUpdate
from app.services.servicio_transportadora import TransportadoraService
from app.config.database import get_db
from app.core.core_auth import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/transportadora',
    tags=['Transportadora']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_transportadoras(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    transportadora_service = TransportadoraService(db)
    output = transportadora_service.exportar_transportadoras(consulta)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=transportadoras.xlsx"})

# Listar transportadora
@router.get('/', response_model=list[TransportadoraResponse], status_code=status.HTTP_200_OK)
def obtener_transportadoras(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    transportadora_service = TransportadoraService(db)
    transportadoras = transportadora_service.obtener_transportadoras()
    return transportadoras

# Crear trailer
@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_transportadora(transportadora: TransportadoraCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    transportadora_service = TransportadoraService(db)
    nueva_transportadora = transportadora_service.crear_transportadora(transportadora)
    if not nueva_transportadora:
        raise HTTPException(status_code=400, detail="Error al crear la transportadora")
    return {"message": "Transportadora creada exitosamente."}

# Actualizar trailer
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_transportadora(id: int, transportadora: TransportadoraUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    transportadora_service = TransportadoraService(db)
    transportadora_actualizada = transportadora_service.actualizar_transportadora(id, transportadora)

    if not transportadora_actualizada:
        raise HTTPException(status_code=404, detail="Transportadora no encontrada")

    return {"message": "Transportadora actualizada exitosamente."}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_transportadora(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    transportadora_service = TransportadoraService(db)
    eliminado = transportadora_service.eliminar_transportadora(id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Transportadora no encontrada")

    return {"message": "Transportadora eliminada exitosamente."}
