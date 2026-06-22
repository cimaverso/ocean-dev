from litestar import Controller, get, post, put
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Response
from litestar.connection import Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from src.core.db import get_db
from src.core.security import guard_autenticado, guard_rol, obtener_payload
from src.features.registro.schemas import RegistroCreate, RegistroUpdate, RegistroResponse
from src.features.registro.services import RegistroService


class RegistroController(Controller):
    path = "/registro"
    tags = ["Registro"]
    dependencies = {"db": Provide(get_db)}
    guards = [guard_autenticado]

    @get("/exportar/ingresos", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_ingresos(self, db: Session, consulta: Optional[str] = None,
                          fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None) -> Response:
        output = RegistroService(db).exportar_ingreso(consulta, fecha_inicio, fecha_fin)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail="No hay datos para exportar.")
        return Response(content=output.read(),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=ingresos.xlsx"})

    @get("/exportar/despachos", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_despachos(self, db: Session, consulta: Optional[str] = None,
                           fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None) -> Response:
        output = RegistroService(db).exportar_despacho(consulta, fecha_inicio, fecha_fin)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail="No hay datos para exportar.")
        return Response(content=output.read(),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=despachos.xlsx"})

    @get("/exportar/servicios", guards=[guard_rol(["ADMINISTRADOR"])], include_in_schema=False)
    def exportar_servicios(self, db: Session, consulta: Optional[str] = None,
                           fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None) -> Response:
        output = RegistroService(db).exportar_servicio(consulta, fecha_inicio, fecha_fin)
        if output.getbuffer().nbytes == 0:
            raise HTTPException(status_code=404, detail="No hay datos para exportar.")
        return Response(content=output.read(),
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment; filename=servicios.xlsx"})

    @get("/consecutivo", include_in_schema=False)
    def obtener_consecutivo(self, db: Session) -> dict:
        proximo_id = RegistroService(db).obtener_consecutivo()
        if not proximo_id:
            raise HTTPException(status_code=404, detail="No se pudo obtener el consecutivo")
        return {"proximo_id": proximo_id}

    @get("/tiquete", include_in_schema=False)
    def obtener_tiquete(self, db: Session) -> dict:
        proximo = RegistroService(db).obtener_consecutivo_tiquete()
        if not proximo:
            raise HTTPException(status_code=404, detail="No se pudo obtener el consecutivo de tiquete")
        return {"proximo_id_tiquete": proximo}

    @get("/")
    def obtener_registros(self, db: Session, estado: Optional[int] = None,
                          tipo: Optional[int] = None, fecha_inicio: Optional[date] = None,
                          fecha_fin: Optional[date] = None) -> list[RegistroResponse]:
        return RegistroService(db).obtener_registros(estado=estado, tipo=tipo,
                                                      fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

    @post("/", status_code=201)
    def crear_registro(self, data: RegistroCreate, db: Session, request: Request) -> dict:
        usuario = obtener_payload(request)
        nuevo = RegistroService(db).crear_registro(data, usuario["usuario_id"])
        if not nuevo:
            raise HTTPException(status_code=400, detail="Error al crear el registro")
        return {"mensaje": "Registro creado exitosamente."}

    @put("/{id:int}")
    def actualizar_registro(self, id: int, data: RegistroUpdate, db: Session, request: Request) -> dict:
        usuario = obtener_payload(request)
        actualizado = RegistroService(db).actualizar_registro(id, data, usuario["usuario_id"])
        if not actualizado:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        return {"mensaje": "Registro actualizado exitosamente."}