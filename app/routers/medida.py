from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.registro.producto.modelo_unidadmedida import UnidadMedidaResponse, UnidadMedidaCreate, UnidadMedidaUpdate
from app.services.servicio_medida import UnidadMedidaService
from app.config.database import get_db
from app.core.core_auth import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/medida',
    tags=['Medida']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_medidas(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    medida_service = UnidadMedidaService(db)
    output = medida_service.exportar_medidas(consulta)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=medidas.xlsx"})

# Listar medidas
@router.get('/',  response_model=list[UnidadMedidaResponse], status_code=status.HTTP_200_OK)
def obtener_medidas(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    medida_service = UnidadMedidaService(db)
    medidas = medida_service.listar_medidas()

    return medidas

# Crear medida
@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_medida(medida: UnidadMedidaCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    medida_service = UnidadMedidaService(db)
    nueva_medida = medida_service.crear_medida(medida)
    if not nueva_medida:
        HTTPException(status_code=400, detail="Error al crear la medida")
    return {"message": "Medida creada exitosamente."}

# Actualizar medida
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_medida(id: int, medida: UnidadMedidaUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    medida_service = UnidadMedidaService(db)
    medida_actualizado = medida_service.actualizar_medida(id, medida)

    if not medida_actualizado:
        raise HTTPException(status_code=404, detail="Medida no encontrada")

    return {"message": "Medida actualizada exitosamente."}

#Eliminar medida
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_medida(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    medida_service = UnidadMedidaService(db)
    eliminado = medida_service.eliminar_medida(id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Medida no encontrada")

    return {"message": "Medida eliminada exitosamente."}  
