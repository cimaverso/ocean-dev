from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.proceso_producto import ProcesoProductoResponse
from app.services.proceso import ProcesoProductoService
from app.config.database import get_db

router = APIRouter(
    prefix='/proceso',
    tags=['Proceso']
)

@router.get('/', include_in_schema=False, response_model=list[ProcesoProductoResponse], status_code=status.HTTP_200_OK)
def obtener_procesos(db: Session = Depends(get_db)):
    return ProcesoProductoService(db).listar_procesos()