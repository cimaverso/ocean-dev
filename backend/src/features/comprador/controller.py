from litestar import Controller, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Response
from sqlalchemy.orm import Session
from typing import Optional

from src.core.db import get_db
from src.core.security import guard_autenticado, guard_rol
from src.features.comprador.schemas import CompradorCreate, CompradorUpdate, CompradorResponse
from src.features.comprador.services import CompradorService


class CompradorController(Controller):
    path = "/comprador"
    tags = ["Comprador"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_autenticado]

    @get("/exportar", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_compradores(self, db: Session, consulta: Optional[str] = None) -> Response:
        output = CompradorService(db).exportar_compradores(consulta)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail="No hay datos para exportar")
        return Response(
            content=output.read(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=compradores.xlsx"},
        )

    @get("/")
    def listar_compradores(self, db: Session) -> list[CompradorResponse]:
        return CompradorService(db).listar_compradores()

    @post("/", status_code=201, guards=[guard_rol(["ADMINISTRADOR"])])
    def crear_comprador(self, data: CompradorCreate, db: Session) -> dict:
        nuevo = CompradorService(db).crear_comprador(data)
        if not nuevo:
            raise HTTPException(status_code=400, detail="Error al crear el comprador")
        return {"message": "Comprador creado exitosamente."}

    @put("/{id:int}", guards=[guard_rol(["ADMINISTRADOR"])])
    def actualizar_comprador(self, id: int, data: CompradorUpdate, db: Session) -> dict:
        actualizado = CompradorService(db).actualizar_comprador(id, data)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Comprador no encontrado")
        return {"message": "Comprador actualizado exitosamente."}