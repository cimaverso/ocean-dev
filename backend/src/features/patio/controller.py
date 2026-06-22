from litestar import Controller, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Response
from sqlalchemy.orm import Session
from typing import Optional

from src.core.db import get_db
from src.core.security import guard_autenticado, guard_rol
from src.features.patio.schemas import PatioCreate, PatioUpdate, PatioResponse
from src.features.patio.services import PatioService


class PatioController(Controller):
    path = "/patio"
    tags = ["Patio"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_autenticado]

    @get("/exportar", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_patios(self, db: Session, consulta: Optional[str] = None) -> Response:
        output = PatioService(db).exportar_patios(consulta)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail="No hay datos para exportar")
        return Response(content=output.read(),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=patios.xlsx"})

    @get("/")
    def listar_patios(self, db: Session) -> list[PatioResponse]:
        return PatioService(db).listar_patios()

    @post("/", status_code=201, guards=[guard_rol(["ADMINISTRADOR"])])
    def crear_patio(self, data: PatioCreate, db: Session) -> dict:
        nuevo = PatioService(db).crear_patio(data)
        if not nuevo:
            raise HTTPException(status_code=400, detail="Error al crear el patio")
        return {"message": "Patio creado exitosamente."}

    @put("/{id:int}", guards=[guard_rol(["ADMINISTRADOR"])])
    def actualizar_patio(self, id: int, data: PatioUpdate, db: Session) -> dict:
        actualizado = PatioService(db).actualizar_patio(id, data)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Patio no encontrado")
        return {"message": "Patio actualizado exitosamente."}