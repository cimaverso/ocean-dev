# routers/entidad.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from fastapi.responses import StreamingResponse
from app.models.registro.entidad.modelo_entidad import EntidadResponse, EntidadCreate, EntidadUpdate
from app.services.servicio_entidad import EntidadService
from app.config.database import get_db
from typing import Optional
from app.core.core_auth import obtener_usuario, verificar_rol

router = APIRouter(
    prefix='/entidad',
    tags=['Entidad']
)

#Exportar entidades
@router.get("/exportar/{tipo}", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_entidad( tipo: int, consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    entidad_service = EntidadService(db)
    output = entidad_service.exportar_entidades(tipo, consulta)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar de tipo {tipo}.")

    filename = {1: "clientes.xlsx", 2: "proveedores.xlsx", 3: "terceros.xlsx"}.get(tipo, "entidad.xlsx")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename={filename}"})

# Listar entidades
@router.get('/{tipo}', response_model=list[EntidadResponse], status_code=status.HTTP_200_OK)
def obtener_entidades(tipo: int, db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    entidad_service = EntidadService(db)
    entidades = entidad_service.listar_entidad(tipo)
    return entidades

# Crear entidad
@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_entidad(entidad: EntidadCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    entidad_service = EntidadService(db)
    nueva_entidad = entidad_service.crear_entidad(entidad)
    if not nueva_entidad:
        raise HTTPException(status_code=400, detail="Error al crear la entidad")
    return {"message": "Entidad creada exitosamente."}

# Actualizar entidad
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_entidad(id: int, entidad: EntidadUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    entidad_service = EntidadService(db)
    entidad_actualizada = entidad_service.actualizar_entidad(id, entidad)

    if not entidad_actualizada:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")

    return {"message": "Entidad actualizada exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_entidad(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    entidad_service = EntidadService(db)
    eliminado = entidad_service.eliminar_entidad(id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Entidad no encontrado")

    return {"message": "Entidad eliminada exitosamente."}
