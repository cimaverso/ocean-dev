from litestar import Controller, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Response
from sqlalchemy.orm import Session
from typing import Optional

from src.core.db import get_db
from src.core.security import guard_autenticado, guard_rol
from src.features.destino.schemas import DestinoCreate, DestinoUpdate, DestinoResponse
from src.features.destino.services import DestinoService


class DestinoController(Controller):
    path = "/destino"
    tags = ["Destino"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_autenticado]

    @get("/exportar", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_destinos(self, db: Session, consulta: Optional[str] = None) -> Response:
        output = DestinoService(db).exportar_destinos(consulta)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail="No hay datos para exportar")
        return Response(content=output.read(),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=destinos.xlsx"})

    @get("/")
    def listar_destinos(self, db: Session) -> list[DestinoResponse]:
        return [DestinoResponse.model_validate(d) for d in DestinoService(db).listar_destinos()]

    @post("/", status_code=201, guards=[guard_rol(["ADMINISTRADOR"])])
    def crear_destino(self, data: DestinoCreate, db: Session) -> dict:
        nuevo = DestinoService(db).crear_destino(data)
        if not nuevo:
            raise HTTPException(status_code=400, detail="Error al crear el destino")
        return {"message": "Destino creado exitosamente."}

    @put("/{id:int}", guards=[guard_rol(["ADMINISTRADOR"])])
    def actualizar_destino(self, id: int, data: DestinoUpdate, db: Session) -> dict:
        actualizado = DestinoService(db).actualizar_destino(id, data)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Destino no encontrado")
        return {"message": "Destino actualizado exitosamente."}