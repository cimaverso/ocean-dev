from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.registro.producto.modelo_procesoproducto import ProcesoProductoResponse
from app.services.servicio_proceso import ProcesoProductoService
from app.config.database import get_db

router = APIRouter(
    prefix='/proceso',
    tags=['Proceso']
)

# Listar procesos
@router.get('/', include_in_schema=False, response_model=list[ProcesoProductoResponse], status_code=status.HTTP_200_OK)
def obtener_procesos(db: Session = Depends(get_db)):
    proceso_service = ProcesoProductoService(db)
    procesos = proceso_service.listar_procesos()

    return procesos