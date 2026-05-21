from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.origen import OrigenResponse, OrigenCreate, OrigenUpdate
from app.services.origen import OrigenService
from app.config.database import get_db
from app.core.security import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/origen',
    tags=['Origen']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_origenes(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    output = OrigenService(db).exportar_origenes(consulta)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail="No hay datos para exportar")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=origenes.xlsx"})

@router.get('/', response_model=list[OrigenResponse], status_code=status.HTTP_200_OK)
def obtener_origenes(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return OrigenService(db).listar_origenes()

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_origen(origen: OrigenCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    nuevo = OrigenService(db).crear_origen(origen)
    if not nuevo:
        raise HTTPException(status_code=400, detail="Error al crear el origen")
    return {"message": "Origen creado exitosamente."}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_origen(id: int, origen: OrigenUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    actualizado = OrigenService(db).actualizar_origen(id, origen)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Origen no encontrado")
    return {"message": "Origen actualizado exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_origen(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    if not OrigenService(db).eliminar_origen(id):
        raise HTTPException(status_code=404, detail="Origen no encontrado")