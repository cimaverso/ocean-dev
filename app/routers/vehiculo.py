from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.registro.modelo_vehiculo import VehiculoResponse, VehiculoCreate, VehiculoUpdate
from app.services.servicio_vehiculo import VehiculoService
from app.config.database import get_db
from fastapi.responses import StreamingResponse
from  typing import Optional
from app.core.core_auth import obtener_usuario, verificar_rol

router = APIRouter(
    prefix='/vehiculo',
    tags=['Vehiculo']
)

#Exportar
@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_vehiculos(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    vehiculo_service = VehiculoService(db)
    output = vehiculo_service.exportar_vehiculos(consulta)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar.")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=vehiculos.xlsx"})

# Listar vehiculos
@router.get('/', response_model=list[VehiculoResponse], status_code=status.HTTP_200_OK)
def obtener_vehiculos(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    vehiculo_service = VehiculoService(db)
    vehiculos = vehiculo_service.obtener_vehiculos()
    return vehiculos

# Crear vehiculo
@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_vehiculos(vehiculo: VehiculoCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    vehiculo_service = VehiculoService(db)
    nuevo_vehiculo = vehiculo_service.crear_vehiculo(vehiculo)
    if not nuevo_vehiculo:
        HTTPException(status_code=400, detail="Error al crear el vehiculo")
    return {"message": "Vehiculo creado exitosamente."}

# Actualizar vehiculo
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_vehiculo(id: int, vehiculo: VehiculoUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    vehiculo_service = VehiculoService(db)
    vehiculo_actualizado = vehiculo_service.actualizar_vehiculo(id, vehiculo)

    if not vehiculo_actualizado:
        raise HTTPException(status_code=404, detail="vehiculo no encontrado")

    return {"message": "Vehiculo actualizado exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_vehiculo(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    vehiculo_service = VehiculoService(db)
    eliminado = vehiculo_service.eliminar_vehiculo(id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")

    return {"message": "Vehiculo eliminado exitosamente."}
