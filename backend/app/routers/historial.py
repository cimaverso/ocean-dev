from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.historial.modelo_historial import HistorialResponse
from app.services.servicio_historial import HistorialService
from app.config.database import get_db
from fastapi.responses import StreamingResponse
from typing import Optional
from app.core.core_auth import verificar_rol
from datetime import date


router = APIRouter(
    prefix='/historial',
    tags=['Historial']
)


@router.get("/exportar", response_class=StreamingResponse, status_code=status.HTTP_200_OK)
def exportar_historial(consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    auditoria_service = HistorialService(db)
    output = auditoria_service.exportar_historial(consulta, fecha_inicio, fecha_fin)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=auditoria.xlsx"})

# Listar historial
@router.get('/',  response_model=list[HistorialResponse], status_code=status.HTTP_200_OK)
def obtener_historial(db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    historial_service = HistorialService(db)
    historial = historial_service.listar_historial()

    return historial
