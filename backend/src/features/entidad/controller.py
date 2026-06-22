from litestar import Controller, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Response
from sqlalchemy.orm import Session
from typing import Optional

from src.core.db import get_db
from src.core.security import guard_autenticado, guard_rol
from src.features.entidad.schemas import EntidadCreate, EntidadUpdate, EntidadResponse
from src.features.entidad.services import EntidadService

FILENAME_MAP = {1: "clientes.xlsx", 2: "proveedores.xlsx", 3: "terceros.xlsx"}


class EntidadController(Controller):
    path = "/entidad"
    tags = ["Entidad"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_autenticado]

    @get("/exportar/{tipo:int}", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_entidades(self, tipo: int, db: Session, consulta: Optional[str] = None) -> Response:
        output = EntidadService(db).exportar_entidades(tipo, consulta)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail=f"No hay datos para exportar de tipo {tipo}.")
        filename = FILENAME_MAP.get(tipo, "entidad.xlsx")
        return Response(content=output.read(),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": f"attachment; filename={filename}"})

    @get("/{tipo:int}")
    def listar_entidades(self, tipo: int, db: Session) -> list[EntidadResponse]:
        return [EntidadResponse.model_validate(e) for e in EntidadService(db).listar_entidad(tipo)]

    @post("/", status_code=201, guards=[guard_rol(["ADMINISTRADOR"])])
    def crear_entidad(self, data: EntidadCreate, db: Session) -> dict:
        nueva = EntidadService(db).crear_entidad(data)
        if not nueva:
            raise HTTPException(status_code=400, detail="Error al crear la entidad")
        return {"message": "Entidad creada exitosamente."}

    @put("/{id:int}", guards=[guard_rol(["ADMINISTRADOR"])])
    def actualizar_entidad(self, id: int, data: EntidadUpdate, db: Session) -> dict:
        actualizada = EntidadService(db).actualizar_entidad(id, data)
        if not actualizada:
            raise HTTPException(status_code=404, detail="Entidad no encontrada")
        return {"message": "Entidad actualizada exitosamente."}