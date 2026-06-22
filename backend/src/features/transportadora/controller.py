from litestar import Controller, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Response
from sqlalchemy.orm import Session
from typing import Optional

from src.core.db import get_db
from src.core.security import guard_autenticado, guard_rol
from src.features.transportadora.schemas import TransportadoraCreate, TransportadoraUpdate, TransportadoraResponse
from src.features.transportadora.services import TransportadoraService


class TransportadoraController(Controller):
    path = "/transportadora"
    tags = ["Transportadora"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_autenticado]

    @get("/exportar", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_transportadoras(self, db: Session, consulta: Optional[str] = None) -> Response:
        output = TransportadoraService(db).exportar_transportadoras(consulta)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail="No hay datos para exportar")
        return Response(content=output.read(),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=transportadoras.xlsx"})

    @get("/")
    def listar_transportadoras(self, db: Session) -> list[TransportadoraResponse]:
        return TransportadoraService(db).obtener_transportadoras()

    @post("/", status_code=201, guards=[guard_rol(["ADMINISTRADOR"])])
    def crear_transportadora(self, data: TransportadoraCreate, db: Session) -> dict:
        nueva = TransportadoraService(db).crear_transportadora(data)
        if not nueva:
            raise HTTPException(status_code=400, detail="Error al crear la transportadora")
        return {"message": "Transportadora creada exitosamente."}

    @put("/{id:int}", guards=[guard_rol(["ADMINISTRADOR"])])
    def actualizar_transportadora(self, id: int, data: TransportadoraUpdate, db: Session) -> dict:
        actualizada = TransportadoraService(db).actualizar_transportadora(id, data)
        if not actualizada:
            raise HTTPException(status_code=404, detail="Transportadora no encontrada")
        return {"message": "Transportadora actualizada exitosamente."}