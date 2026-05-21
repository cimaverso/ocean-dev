from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.patio import PatioResponse, PatioCreate, PatioUpdate
from app.services.patio import PatioService
from app.config.database import get_db
from app.core.security import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/patio',
    tags=['Patio']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_patios(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    output = PatioService(db).exportar_patios(consulta)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail="No hay datos para exportar")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=patios.xlsx"})

@router.get('/', response_model=list[PatioResponse], status_code=status.HTTP_200_OK)
def obtener_patios(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return PatioService(db).listar_patios()

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_patio(patio: PatioCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    nuevo = PatioService(db).crear_patio(patio)
    if not nuevo:
        raise HTTPException(status_code=400, detail="Error al crear el patio")
    return {"message": "Patio creado exitosamente."}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_patio(id: int, patio: PatioUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    actualizado = PatioService(db).actualizar_patio(id, patio)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Patio no encontrado")
    return {"message": "Patio actualizado exitosamente."}

