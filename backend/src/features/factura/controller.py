from litestar import Controller, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Response
from sqlalchemy.orm import Session
from typing import Optional

from src.core.db import get_db
from src.core.security import guard_autenticado, guard_rol
from src.features.factura.schemas import FacturaCreate, FacturaUpdate, FacturaResponse
from src.features.factura.services import FacturaService


class FacturaController(Controller):
    path = "/factura"
    tags = ["Factura"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_autenticado]

    @get("/exportar", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_facturas(self, db: Session, consulta: Optional[str] = None) -> Response:
        output = FacturaService(db).exportar_facturas(consulta)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail="No hay datos para exportar")
        return Response(content=output.read(),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=facturas.xlsx"})

    @get("/")
    def listar_facturas(self, db: Session) -> list[FacturaResponse]:
        return [FacturaResponse.model_validate(f) for f in FacturaService(db).listar_facturas()]

    @post("/", status_code=201, guards=[guard_rol(["ADMINISTRADOR"])])
    def crear_factura(self, data: FacturaCreate, db: Session) -> dict:
        nuevo = FacturaService(db).crear_factura(data)
        if not nuevo:
            raise HTTPException(status_code=400, detail="Error al crear la factura")
        return {"message": "Factura creada exitosamente."}

    @put("/{id:int}", guards=[guard_rol(["ADMINISTRADOR"])])
    def actualizar_factura(self, id: int, data: FacturaUpdate, db: Session) -> dict:
        actualizada = FacturaService(db).actualizar_factura(id, data)
        if not actualizada:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        return {"message": "Factura actualizada exitosamente."}