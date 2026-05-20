from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.registro.modelo_conductor import ConductorResponse, ConductorCreate, ConductorUpdate
from app.services.servicio_conductor import ConductorService
from app.config.database import get_db
from typing import Optional
from fastapi.responses import StreamingResponse
from app.core.core_auth import verificar_rol, obtener_usuario

router = APIRouter(
    prefix='/conductor',
    tags=['Conductor']
)

#Exportar conductores
@router.get("/exportar", include_in_schema=False, response_class=StreamingResponse, status_code=status.HTTP_200_OK)
def exportar_conductores(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    conductor_service = ConductorService(db)
    output = conductor_service.exportar_conductores(consulta)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=conductores.xlsx"})

# Listar conductores
@router.get('/', response_model=list[ConductorResponse], status_code=status.HTTP_200_OK)
def obtener_conductores(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    conductor_service = ConductorService(db)
    conductores = conductor_service.listar_conductores()
    return conductores

# Crear conductor
@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_conductor(conductor: ConductorCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    conductor_service = ConductorService(db)
    nuevo_conductor = conductor_service.crear_conductor(conductor)
    if not nuevo_conductor:
        raise HTTPException(status_code=400, detail="Error al crear el conductor")
    
    return {"message": "Conductor creado exitosamente."}

# Actualizar conductor
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_conductor(id: int, conductor: ConductorUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    conductor_service = ConductorService(db)
    conductor_actualizado = conductor_service.actualizar_conductor(id, conductor)

    if not conductor_actualizado:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    return {"message": "Conductor actualizado exitosamente."}

# Eliminar conductor
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_conductor(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    conductor_service = ConductorService(db)
    eliminado = conductor_service.eliminar_conductor(id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    return {"message": "Conductor eliminado exitosamente."}
