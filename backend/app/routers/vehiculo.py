from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.vehiculo import VehiculoResponse, VehiculoCreate, VehiculoUpdate
from app.services.vehiculo import VehiculoService
from app.config.database import get_db
from app.core.security import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/vehiculo',
    tags=['Vehiculo']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_vehiculos(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    output = VehiculoService(db).exportar_vehiculos(consulta)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail="No hay datos para exportar.")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=vehiculos.xlsx"})

@router.get('/', response_model=list[VehiculoResponse], status_code=status.HTTP_200_OK)
def obtener_vehiculos(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return VehiculoService(db).obtener_vehiculos()

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_vehiculos(vehiculo: VehiculoCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    nuevo = VehiculoService(db).crear_vehiculo(vehiculo)
    if not nuevo:
        raise HTTPException(status_code=400, detail="Error al crear el vehiculo")
    return {"message": "Vehiculo creado exitosamente."}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_vehiculo(id: int, vehiculo: VehiculoUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    actualizado = VehiculoService(db).actualizar_vehiculo(id, vehiculo)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")
    return {"message": "Vehiculo actualizado exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_vehiculo(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    if not VehiculoService(db).eliminar_vehiculo(id):
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")