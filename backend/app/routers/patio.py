from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.registro.modelo_patio import PatioResponse, PatioCreate, PatioUpdate
from app.services.servicio_patio import PatioService
from app.config.database import get_db
from app.core.core_auth import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/patio',
    tags=['Patio']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_patios(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    patio_service = PatioService(db)
    output = patio_service.exportar_patios(consulta)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=patios.xlsx"})

# Listar patios
@router.get('/', response_model=list[PatioResponse], status_code=status.HTTP_200_OK)
def obtener_patios(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    patio_service = PatioService(db)
    patios = patio_service.listar_patios()


    return patios

# Crear patio
@router.post('/', response_model=PatioResponse, status_code=status.HTTP_201_CREATED)
def crear_patio(patio: PatioCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    patio_service = PatioService(db)
    nuevo_patio = patio_service.crear_patio(patio)
    if not nuevo_patio:
        raise HTTPException(status_code=400, detail="Error al crear el patio")
    
    return {"message": "Patio creado exitosamente."}

# Actualizar patio
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_patio(id: int, patio: PatioUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    patio_service = PatioService(db)
    patio_actualizado = patio_service.actualizar_patio(id, patio)

    if not patio_actualizado:
        raise HTTPException(status_code=404, detail="Patio no encontrado")

    return {"message": "Patio actualizado exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_patio(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    patio_service = PatioService(db)
    eliminado = patio_service.eliminar_patio(id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Patio no encontrado")

    return {"message": "Patio eliminado exitosamente."} 
