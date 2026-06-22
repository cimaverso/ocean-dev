from litestar import Controller, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Response
from sqlalchemy.orm import Session
from typing import Optional

from src.core.db import get_db
from src.core.security import guard_autenticado, guard_rol
from src.features.producto.schemas import ProductoCreate, ProductoUpdate, ProductoResponse, ProcesoProductoResponse
from src.features.producto.services import ProductoService

FILENAME_MAP = {1: "productos.xlsx", 2: "servicios.xlsx"}


class ProductoController(Controller):
    path = "/producto"
    tags = ["Productos"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_autenticado]

    @get("/exportar/{tipo:int}", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_productos(self, tipo: int, db: Session, consulta: Optional[str] = None) -> Response:
        output = ProductoService(db).exportar_productos(tipo, consulta)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail=f"No hay datos para exportar de tipo {tipo}.")
        filename = FILENAME_MAP.get(tipo, "producto.xlsx")
        return Response(content=output.read(),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": f"attachment; filename={filename}"})

    @get("/proceso", include_in_schema=False)
    def listar_procesos(self, db: Session) -> list[ProcesoProductoResponse]:
        return ProductoService(db).listar_procesos()

    @get("/{tipo:int}")
    def listar_productos_tipo(self, tipo: int, db: Session) -> list[ProductoResponse]:
        return ProductoService(db).listar_productos_tipo(tipo)

    @post("/", status_code=201, guards=[guard_rol(["ADMINISTRADOR"])])
    def crear_producto(self, data: ProductoCreate, db: Session) -> dict:
        nuevo = ProductoService(db).crear_producto(data)
        if not nuevo:
            raise HTTPException(status_code=400, detail="Error al crear el producto")
        return {"message": "Producto creado exitosamente."}

    @put("/{id:int}", guards=[guard_rol(["ADMINISTRADOR"])])
    def actualizar_producto(self, id: int, data: ProductoUpdate, db: Session) -> dict:
        actualizado = ProductoService(db).actualizar_producto(id, data)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return {"message": "Producto actualizado exitosamente."}