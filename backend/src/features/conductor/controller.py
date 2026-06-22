from litestar import Controller, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Response
from sqlalchemy.orm import Session
from typing import Optional

from src.core.db import get_db
from src.core.security import guard_autenticado, guard_rol
from src.features.conductor.schemas import ConductorCreate, ConductorUpdate, ConductorResponse
from src.features.conductor.services import ConductorService


class ConductorController(Controller):
    path = "/conductor"
    tags = ["Conductor"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_autenticado]

    @get("/exportar", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_conductores(self, db: Session, consulta: Optional[str] = None) -> Response:
        output = ConductorService(db).exportar_conductores(consulta)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail="No hay datos para exportar")
        return Response(content=output.read(),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=conductores.xlsx"})

    @get("/")
    def listar_conductores(self, db: Session) -> list[ConductorResponse]:
        return [ConductorResponse.model_validate(c) for c in ConductorService(db).listar_conductores()]

    @post("/", status_code=201, guards=[guard_rol(["ADMINISTRADOR"])])
    def crear_conductor(self, data: ConductorCreate, db: Session) -> dict:
        nuevo = ConductorService(db).crear_conductor(data)
        if not nuevo:
            raise HTTPException(status_code=400, detail="Error al crear el conductor")
        return {"message": "Conductor creado exitosamente."}

    @put("/{id:int}", guards=[guard_rol(["ADMINISTRADOR"])])
    def actualizar_conductor(self, id: int, data: ConductorUpdate, db: Session) -> dict:
        actualizado = ConductorService(db).actualizar_conductor(id, data)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Conductor no encontrado")
        return {"message": "Conductor actualizado exitosamente."}