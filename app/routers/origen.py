# routers/origen.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.registro.modelo_origen import OrigenResponse, OrigenCreate, OrigenUpdate
from app.services.servicio_origen import OrigenService
from app.config.database import get_db
from app.core.core_auth import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/origen',
    tags=['Origen']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_origenes(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    origen_service = OrigenService(db)
    output = origen_service.exportar_origenes(consulta)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=origenes.xlsx"})

# Listar origenes
@router.get('/', response_model=list[OrigenResponse], status_code=status.HTTP_200_OK)
def obtener_origenes(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    origen_service = OrigenService(db)
    origenes = origen_service.listar_origenes()

    return origenes

# Crear origen
@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_origen(origen: OrigenCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    origen_service = OrigenService(db)
    nuevo_origen = origen_service.crear_origen(origen)
    if not nuevo_origen:
        raise HTTPException(status_code=400, detail="Error al crear el origen")
    
    return {"message": "Origen creado exitosamente."}

# Actualizar origen
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_origen(id: int, origen: OrigenUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    origen_service = OrigenService(db)
    origen_actualizado = origen_service.actualizar_origen(id, origen)

    if not origen_actualizado:
        raise HTTPException(status_code=404, detail="Origen no encontrado")

    return {"message": "Origen actualizado exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_origen(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    origen_service = OrigenService(db)
    eliminado = origen_service.eliminar_origen(id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Origen no encontrado")

    return {"message": "Origen eliminado exitosamente."}
