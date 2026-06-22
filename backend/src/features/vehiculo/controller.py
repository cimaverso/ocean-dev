from litestar import Controller, get, post, put, delete
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Response
from sqlalchemy.orm import Session
from typing import Optional

from src.core.db import get_db
from src.core.security import guard_autenticado, guard_rol
from src.features.vehiculo.schemas import VehiculoCreate, VehiculoUpdate, VehiculoResponse
from src.features.vehiculo.services import VehiculoService


class VehiculoController(Controller):
    path = "/vehiculo"
    tags = ["Vehiculo"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_autenticado]

    @get("/exportar", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_vehiculos(self, db: Session, consulta: Optional[str] = None) -> Response:
        output = VehiculoService(db).exportar_vehiculos(consulta)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail="No hay datos para exportar.")
        return Response(content=output.read(),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=vehiculos.xlsx"})

    @get("/")
    def obtener_vehiculos(self, db: Session) -> list[VehiculoResponse]:
        return [VehiculoResponse.model_validate(v) for v in VehiculoService(db).obtener_vehiculos()]

    @post("/", status_code=201, guards=[guard_rol(["ADMINISTRADOR"])])
    def crear_vehiculo(self, data: VehiculoCreate, db: Session) -> dict:
        nuevo = VehiculoService(db).crear_vehiculo(data)
        if not nuevo:
            raise HTTPException(status_code=400, detail="Error al crear el vehiculo")
        return {"message": "Vehiculo creado exitosamente."}

    @put("/{id:int}", guards=[guard_rol(["ADMINISTRADOR"])])
    def actualizar_vehiculo(self, id: int, data: VehiculoUpdate, db: Session) -> dict:
        actualizado = VehiculoService(db).actualizar_vehiculo(id, data)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Vehiculo no encontrado")
        return {"message": "Vehiculo actualizado exitosamente."}

    @delete("/{id:int}", status_code=204, guards=[guard_rol(["ADMINISTRADOR"])])
    def eliminar_vehiculo(self, id: int, db: Session) -> None:
        eliminado = VehiculoService(db).eliminar_vehiculo(id)
        if not eliminado:
            raise HTTPException(status_code=404, detail="Vehiculo no encontrado")