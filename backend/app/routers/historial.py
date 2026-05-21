from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.historial import HistorialResponse
from app.services.historial import HistorialService
from app.config.database import get_db
from app.core.security import verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import date

router = APIRouter(
    prefix='/historial',
    tags=['Historial']
)

@router.get("/exportar", response_class=StreamingResponse, status_code=status.HTTP_200_OK)
def exportar_historial(consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    output = HistorialService(db).exportar_historial(consulta, fecha_inicio, fecha_fin)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail="No hay datos para exportar")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=auditoria.xlsx"})

@router.get('/', response_model=list[HistorialResponse], status_code=status.HTTP_200_OK)
def obtener_historial(db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    return HistorialService(db).listar_historial()