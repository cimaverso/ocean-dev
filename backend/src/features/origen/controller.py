from litestar import Controller, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Response
from sqlalchemy.orm import Session
from typing import Optional

from src.core.db import get_db
from src.core.security import guard_autenticado, guard_rol
from src.features.origen.schemas import OrigenCreate, OrigenUpdate, OrigenResponse
from src.features.origen.services import OrigenService


class OrigenController(Controller):
    path = "/origen"
    tags = ["Origen"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_autenticado]

    @get("/exportar", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_origenes(self, db: Session, consulta: Optional[str] = None) -> Response:
        output = OrigenService(db).exportar_origenes(consulta)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail="No hay datos para exportar")
        return Response(content=output.read(),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=origenes.xlsx"})

    @get("/")
    def listar_origenes(self, db: Session) -> list[OrigenResponse]:
        return OrigenService(db).listar_origenes()

    @post("/", status_code=201, guards=[guard_rol(["ADMINISTRADOR"])])
    def crear_origen(self, data: OrigenCreate, db: Session) -> dict:
        nuevo = OrigenService(db).crear_origen(data)
        if not nuevo:
            raise HTTPException(status_code=400, detail="Error al crear el origen")
        return {"message": "Origen creado exitosamente."}

    @put("/{id:int}", guards=[guard_rol(["ADMINISTRADOR"])])
    def actualizar_origen(self, id: int, data: OrigenUpdate, db: Session) -> dict:
        actualizado = OrigenService(db).actualizar_origen(id, data)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Origen no encontrado")
        return {"message": "Origen actualizado exitosamente."}