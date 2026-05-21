from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.conductor import ConductorResponse, ConductorCreate, ConductorUpdate
from app.services.conductor import ConductorService
from app.config.database import get_db
from app.core.security import verificar_rol, obtener_usuario
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/conductor',
    tags=['Conductor']
)

@router.get("/exportar", include_in_schema=False, response_class=StreamingResponse, status_code=status.HTTP_200_OK)
def exportar_conductores(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    output = ConductorService(db).exportar_conductores(consulta)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail="No hay datos para exportar")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=conductores.xlsx"})

@router.get('/', response_model=list[ConductorResponse], status_code=status.HTTP_200_OK)
def obtener_conductores(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return ConductorService(db).listar_conductores()

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_conductor(conductor: ConductorCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    nuevo = ConductorService(db).crear_conductor(conductor)
    if not nuevo:
        raise HTTPException(status_code=400, detail="Error al crear el conductor")
    return {"message": "Conductor creado exitosamente."}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_conductor(id: int, conductor: ConductorUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    actualizado = ConductorService(db).actualizar_conductor(id, conductor)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return {"message": "Conductor actualizado exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_conductor(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["ADMINISTRADOR"]))):
    if not ConductorService(db).eliminar_conductor(id):
        raise HTTPException(status_code=404, detail="Conductor no encontrado")