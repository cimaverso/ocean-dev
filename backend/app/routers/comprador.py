from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.comprador import CompradorResponse, CompradorCreate, CompradorUpdate
from app.services.comprador import CompradorService
from app.config.database import get_db
from app.core.security import verificar_rol, obtener_usuario
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/comprador',
    tags=['Comprador']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_compradores(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    comprador_service = CompradorService(db)
    output = comprador_service.exportar_compradores(consulta)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail="No hay datos para exportar")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=compradores.xlsx"})

@router.get('/', response_model=list[CompradorResponse], status_code=status.HTTP_200_OK)
def obtener_compradores(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return CompradorService(db).listar_compradores()

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_comprador(comprador: CompradorCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    nuevo = CompradorService(db).crear_comprador(comprador)
    if not nuevo:
        raise HTTPException(status_code=400, detail="Error al crear el comprador")
    return {"message": "Comprador creado exitosamente."}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_comprador(id: int, comprador: CompradorUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    actualizado = CompradorService(db).actualizar_comprador(id, comprador)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Comprador no encontrado")
    return {"message": "Comprador actualizado exitosamente."}

