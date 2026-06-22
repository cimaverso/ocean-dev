from litestar import Controller, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Response
from sqlalchemy.orm import Session
from typing import Optional

from src.core.db import get_db
from src.core.security import guard_autenticado, guard_rol
from src.features.medida.schemas import UnidadMedidaCreate, UnidadMedidaUpdate, UnidadMedidaResponse
from src.features.medida.services import UnidadMedidaService


class MedidaController(Controller):
    path = "/medida"
    tags = ["Medida"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_autenticado]

    @get("/exportar", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_medidas(self, db: Session, consulta: Optional[str] = None) -> Response:
        output = UnidadMedidaService(db).exportar_medidas(consulta)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail="No hay datos para exportar")
        return Response(content=output.read(),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=medidas.xlsx"})

    @get("/")
    def listar_medidas(self, db: Session) -> list[UnidadMedidaResponse]:
        return UnidadMedidaService(db).listar_medidas()

    @post("/", status_code=201, guards=[guard_rol(["ADMINISTRADOR"])])
    def crear_medida(self, data: UnidadMedidaCreate, db: Session) -> dict:
        nuevo = UnidadMedidaService(db).crear_medida(data)
        if not nuevo:
            raise HTTPException(status_code=400, detail="Error al crear la medida")
        return {"message": "Medida creada exitosamente."}

    @put("/{id:int}", guards=[guard_rol(["ADMINISTRADOR"])])
    def actualizar_medida(self, id: int, data: UnidadMedidaUpdate, db: Session) -> dict:
        actualizada = UnidadMedidaService(db).actualizar_medida(id, data)
        if not actualizada:
            raise HTTPException(status_code=404, detail="Medida no encontrada")
        return {"message": "Medida actualizada exitosamente."}