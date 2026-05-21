from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.unidad_medida import UnidadMedidaResponse, UnidadMedidaCreate, UnidadMedidaUpdate
from app.services.medida import UnidadMedidaService
from app.config.database import get_db
from app.core.security import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/medida',
    tags=['Medida']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_medidas(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    output = UnidadMedidaService(db).exportar_medidas(consulta)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail="No hay datos para exportar")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=medidas.xlsx"})

@router.get('/', response_model=list[UnidadMedidaResponse], status_code=status.HTTP_200_OK)
def obtener_medidas(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return UnidadMedidaService(db).listar_medidas()

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_medida(medida: UnidadMedidaCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    nuevo = UnidadMedidaService(db).crear_medida(medida)
    if not nuevo:
        raise HTTPException(status_code=400, detail="Error al crear la medida")
    return {"message": "Medida creada exitosamente."}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_medida(id: int, medida: UnidadMedidaUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    actualizada = UnidadMedidaService(db).actualizar_medida(id, medida)
    if not actualizada:
        raise HTTPException(status_code=404, detail="Medida no encontrada")
    return {"message": "Medida actualizada exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_medida(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    if not UnidadMedidaService(db).eliminar_medida(id):
        raise HTTPException(status_code=404, detail="Medida no encontrada")