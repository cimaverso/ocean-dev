from litestar import Controller, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Response
from sqlalchemy.orm import Session
from typing import Optional

from src.core.db import get_db
from src.core.security import guard_autenticado, guard_rol
from src.features.trailer.schemas import TrailerCreate, TrailerUpdate, TrailerResponse
from src.features.trailer.services import TrailerService


class TrailerController(Controller):
    path = "/trailer"
    tags = ["Trailer"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_autenticado]

    @get("/exportar", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_trailers(self, db: Session, consulta: Optional[str] = None) -> Response:
        output = TrailerService(db).exportar_trailers(consulta)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail="No hay datos para exportar")
        return Response(
            content=output.read(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=trailers.xlsx"},
        )

    @get("/")
    def obtener_trailers(self, db: Session) -> list[TrailerResponse]:
        return TrailerService(db).obtener_trailers()

    @post("/", status_code=201, guards=[guard_rol(["ADMINISTRADOR"])])
    def crear_trailer(self, data: TrailerCreate, db: Session) -> dict:
        nuevo = TrailerService(db).crear_trailer(data)
        if not nuevo:
            raise HTTPException(status_code=400, detail="Error al crear el trailer")
        return {"message": "Trailer creado exitosamente."}

    @put("/{id:int}", guards=[guard_rol(["ADMINISTRADOR"])])
    def actualizar_trailer(self, id: int, data: TrailerUpdate, db: Session) -> dict:
        actualizado = TrailerService(db).actualizar_trailer(id, data)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Trailer no encontrado")
        return {"message": "Trailer actualizado exitosamente."}