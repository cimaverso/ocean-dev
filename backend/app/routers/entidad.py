from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from app.schemas.entidad import EntidadResponse, EntidadCreate, EntidadUpdate
from app.services.entidad import EntidadService
from app.config.database import get_db
from app.core.security import obtener_usuario, verificar_rol
from typing import Optional

router = APIRouter(
    prefix='/entidad',
    tags=['Entidad']
)

@router.get("/exportar/{tipo}", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_entidad(tipo: int, consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    output = EntidadService(db).exportar_entidades(tipo, consulta)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar de tipo {tipo}.")
    filename = {1: "clientes.xlsx", 2: "proveedores.xlsx", 3: "terceros.xlsx"}.get(tipo, "entidad.xlsx")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename={filename}"})

@router.get('/{tipo}', response_model=list[EntidadResponse], status_code=status.HTTP_200_OK)
def obtener_entidades(tipo: int, db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return EntidadService(db).listar_entidad(tipo)

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_entidad(entidad: EntidadCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    nueva = EntidadService(db).crear_entidad(entidad)
    if not nueva:
        raise HTTPException(status_code=400, detail="Error al crear la entidad")
    return {"message": "Entidad creada exitosamente."}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_entidad(id: int, entidad: EntidadUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    actualizada = EntidadService(db).actualizar_entidad(id, entidad)
    if not actualizada:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")
    return {"message": "Entidad actualizada exitosamente."}

