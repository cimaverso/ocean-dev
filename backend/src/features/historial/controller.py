from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from src.core.db import get_db
from src.core.security import guard_rol
from src.features.historial.schemas import HistorialResponse
from src.features.historial.services import HistorialService


class HistorialController(Controller):
    path = "/historial"
    tags = ["Historial"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_rol(["ADMINISTRADOR"])]

    @get("/exportar")
    def exportar_historial(self, db: Session, consulta: Optional[str] = None,
                           fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None) -> Response:
        output = HistorialService(db).exportar_historial(consulta, fecha_inicio, fecha_fin)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail="No hay datos para exportar")
        return Response(content=output.read(),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=auditoria.xlsx"})

    @get("/")
    def listar_historial(self, db: Session) -> list[HistorialResponse]:
        return HistorialService(db).listar_historial()