from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, desc, or_, text
from datetime import date, datetime
from typing import Optional
import pandas as pd
import io

from src.features.registro.models import Registro
from src.features.historial.models import Historial
from src.features.vehiculo.models import Vehiculo
from src.features.conductor.models import Conductor
from src.features.entidad.models import Entidad
from src.features.producto.models import Producto
from src.features.comprador.models import Comprador
from src.features.transportadora.models import Transportadora
from src.features.origen.models import Origen
from src.features.destino.models import Destino
from src.features.patio.models import Patio
from src.features.factura.models import Factura
from src.features.registro.schemas import RegistroCreate, RegistroUpdate


def _load_all(query):
    return query.options(
        selectinload(Registro.tipo),
        selectinload(Registro.vehiculo),
        selectinload(Registro.trailer),
        selectinload(Registro.conductor),
        selectinload(Registro.entidad).selectinload(Entidad.tipo),
        selectinload(Registro.producto).selectinload(Producto.unidad_medida),
        selectinload(Registro.producto).selectinload(Producto.tipo_producto),
        selectinload(Registro.producto).selectinload(Producto.proceso_producto),
        selectinload(Registro.comprador),
        selectinload(Registro.transportadora),
        selectinload(Registro.origen),
        selectinload(Registro.destino),
        selectinload(Registro.patio),
        selectinload(Registro.factura),
    )


def _excel_output(df, sheet_name):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        sheet = writer.book[sheet_name]
        for col in sheet.columns:
            max_length = max((len(str(cell.value)) for cell in col if cell.value), default=0)
            sheet.column_dimensions[col[0].column_letter].width = max_length + 2
    output.seek(0)
    return output


class RegistroService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_registros(self, estado: Optional[int] = None, tipo: Optional[int] = None,
                          fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None):
        query = _load_all(select(Registro))
        if estado is not None:
            query = query.where(Registro.estado == estado)
        if tipo is not None:
            query = query.where(Registro.tipo_id == tipo)
        if fecha_inicio:
            query = query.where(Registro.fecha_salida >= fecha_inicio)
        if fecha_fin:
            query = query.where(Registro.fecha_salida <= fecha_fin)
        return self.db.execute(
            query.order_by(desc(Registro.fecha_entrada), desc(Registro.hora_entrada))
        ).scalars().all()

    def exportar_ingreso(self, consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None):
        query = select(Registro).where(Registro.tipo_id == 1, Registro.estado == 1)
        if fecha_inicio and fecha_fin:
            query = query.where(Registro.fecha_salida.between(fecha_inicio, fecha_fin))
        elif fecha_inicio:
            query = query.where(Registro.fecha_salida >= fecha_inicio)
        elif fecha_fin:
            query = query.where(Registro.fecha_salida <= fecha_fin)
        if consulta:
            query = query.where(or_(
                Registro.origen.has(Origen.nombre.ilike(f"%{consulta}%")),
                Registro.factura.has(Factura.fecha.ilike(f"%{consulta}%")),
                Registro.vehiculo.has(Vehiculo.placa.ilike(f"%{consulta}%")),
                Registro.conductor.has(Conductor.nombre.ilike(f"%{consulta}%")),
                Registro.entidad.has(Entidad.nombre.ilike(f"%{consulta}%")),
                Registro.comprador.has(Comprador.nombre.ilike(f"%{consulta}%")),
                Registro.producto.has(Producto.nombre.ilike(f"%{consulta}%")),
                Registro.patio.has(Patio.nombre.ilike(f"%{consulta}%")),
                Registro.observaciones.ilike(f"%{consulta}%")
            ))
        ingresos = self.db.execute(query).scalars().all()
        data = [{'Tiquete': r.tiquete, 'Registro': r.consecutivo, 'Tipo': r.tipo.nombre,
                 'Facturado': r.factura.fecha if r.factura else None,
                 'Origen': r.origen.nombre if r.origen else None,
                 'Fecha Entrada': r.fecha_entrada.strftime("%Y-%m-%d") if r.fecha_entrada else '',
                 'Hora Entrada': r.hora_entrada.strftime("%I:%M %p") if r.hora_entrada else '',
                 'Fecha Salida': r.fecha_salida.strftime("%Y-%m-%d") if r.fecha_salida else '',
                 'Hora Salida': r.hora_salida.strftime("%I:%M %p") if r.hora_salida else '',
                 'Placa': r.vehiculo.placa if r.vehiculo else None,
                 'Trailer': r.trailer.placa if r.trailer else None,
                 'Conductor': r.conductor.nombre if r.conductor else None,
                 'Cedula Conductor': r.conductor.cedula if r.conductor else None,
                 'Codigo Proveedor': r.entidad.codigo if r.entidad else None,
                 'Proveedor': r.entidad.nombre if r.entidad else None,
                 'Codigo Comprador': r.comprador.codigo if r.comprador else None,
                 'Comprador': r.comprador.nombre if r.comprador else None,
                 'Codigo Producto': r.producto.codigo if r.producto else None,
                 'Producto': r.producto.nombre if r.producto else None,
                 'Peso Bruto': int(r.peso_bruto) if r.peso_bruto else None,
                 'Peso Tara': int(r.peso_tara) if r.peso_tara else None,
                 'Peso Neto': int(r.peso_neto) if r.peso_neto else None,
                 'Patio': r.patio.nombre if r.patio else None,
                 'Observaciones': r.observaciones} for r in ingresos]
        return _excel_output(pd.DataFrame(data), "Ingresos")

    def exportar_despacho(self, consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None):
        query = select(Registro).where(Registro.tipo_id == 2, Registro.estado == 1)
        if fecha_inicio and fecha_fin:
            query = query.where(Registro.fecha_entrada.between(fecha_inicio, fecha_fin))
        elif fecha_inicio:
            query = query.where(Registro.fecha_entrada >= fecha_inicio)
        elif fecha_fin:
            query = query.where(Registro.fecha_entrada <= fecha_fin)
        if consulta:
            query = query.where(or_(
                Registro.vehiculo.has(Vehiculo.placa.ilike(f"%{consulta}%")),
                Registro.conductor.has(Conductor.nombre.ilike(f"%{consulta}%")),
                Registro.entidad.has(Entidad.nombre.ilike(f"%{consulta}%")),
                Registro.destino.has(Destino.nombre.ilike(f"%{consulta}%")),
                Registro.producto.has(Producto.nombre.ilike(f"%{consulta}%")),
                Registro.transportadora.has(Transportadora.nombre.ilike(f"%{consulta}%")),
                Registro.orden.ilike(f"%{consulta}%"),
                Registro.observaciones.ilike(f"%{consulta}%")
            ))
        despachos = self.db.execute(query).scalars().all()
        data = [{'Tiquete': r.tiquete, 'Registro': r.consecutivo, 'Tipo': r.tipo.nombre,
                 'Fecha Entrada': r.fecha_entrada.strftime("%Y-%m-%d") if r.fecha_entrada else '',
                 'Hora Entrada': r.hora_entrada.strftime("%I:%M %p") if r.hora_entrada else '',
                 'Fecha Salida': r.fecha_salida.strftime("%Y-%m-%d") if r.fecha_salida else '',
                 'Hora Salida': r.hora_salida.strftime("%I:%M %p") if r.hora_salida else '',
                 'Placa': r.vehiculo.placa if r.vehiculo else None,
                 'Conductor': r.conductor.nombre if r.conductor else None,
                 'Cliente': r.entidad.nombre if r.entidad else None,
                 'Destino': r.destino.nombre if r.destino else None,
                 'Producto': r.producto.nombre if r.producto else None,
                 'Peso Bruto': int(r.peso_bruto) if r.peso_bruto else None,
                 'Peso Tara': int(r.peso_tara) if r.peso_tara else None,
                 'Peso Neto': int(r.peso_neto) if r.peso_neto else None,
                 'Transportadora': r.transportadora.nombre if r.transportadora else None,
                 'Orden': r.orden, 'Precinto': r.precinto,
                 'Observaciones': r.observaciones} for r in despachos]
        return _excel_output(pd.DataFrame(data), "Despachos")

    def exportar_servicio(self, consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None):
        query = select(Registro).where(Registro.tipo_id == 3, Registro.estado == 1)
        if fecha_inicio and fecha_fin:
            query = query.where(Registro.fecha_entrada.between(fecha_inicio, fecha_fin))
        elif fecha_inicio:
            query = query.where(Registro.fecha_entrada >= fecha_inicio)
        elif fecha_fin:
            query = query.where(Registro.fecha_entrada <= fecha_fin)
        if consulta:
            query = query.where(or_(
                Registro.vehiculo.has(Vehiculo.placa.ilike(f"%{consulta}%")),
                Registro.conductor.has(Conductor.nombre.ilike(f"%{consulta}%")),
                Registro.entidad.has(Entidad.nombre.ilike(f"%{consulta}%")),
                Registro.producto.has(Producto.nombre.ilike(f"%{consulta}%")),
                Registro.observaciones.ilike(f"%{consulta}%")
            ))
        servicios = self.db.execute(query).scalars().all()
        data = [{'Tiquete': r.tiquete, 'Registro': r.consecutivo,
                 'Fecha Entrada': r.fecha_entrada.strftime("%Y-%m-%d") if r.fecha_entrada else '',
                 'Hora Entrada': r.hora_entrada.strftime("%I:%M %p") if r.hora_entrada else '',
                 'Fecha Salida': r.fecha_salida.strftime("%Y-%m-%d") if r.fecha_salida else '',
                 'Hora Salida': r.hora_salida.strftime("%I:%M %p") if r.hora_salida else '',
                 'Placa': r.vehiculo.placa if r.vehiculo else None,
                 'Conductor': r.conductor.nombre if r.conductor else None,
                 'Tercero': r.entidad.nombre if r.entidad else None,
                 'Producto': r.producto.nombre if r.producto else None,
                 'Unidad': r.producto.unidad_medida.nombre if r.producto and r.producto.unidad_medida else None,
                 'Cantidad': r.cantidad,
                 'Peso Bruto': int(r.peso_bruto) if r.peso_bruto else None,
                 'Peso Neto': int(r.peso_neto) if r.peso_neto else None,
                 'Observaciones': r.observaciones} for r in servicios]
        return _excel_output(pd.DataFrame(data), "Servicios")

    def obtener_consecutivo(self):
        return self.db.execute(text("SELECT nextval('reg_consecutivo_seq')")).scalar()

    def obtener_consecutivo_tiquete(self):
        return self.db.execute(text("SELECT nextval('reg_tiquete_seq')")).scalar()

    def crear_registro(self, data: RegistroCreate, usuario_id: int) -> Registro:
        payload = data.model_dump()
        payload['estado'] = 0
        nuevo = Registro(**payload)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        self.db.add(Historial(
            accion="CREADO",
            fecha=datetime.now().date(),
            hora=datetime.now().time().replace(microsecond=0),
            usuario_id=usuario_id,
            registro_id=nuevo.id
        ))
        self.db.commit()
        return nuevo

    def actualizar_registro(self, id: int, data: RegistroUpdate, usuario_id: int) -> Registro | None:
        registro = self.db.execute(select(Registro).where(Registro.id == id)).scalar_one_or_none()
        if not registro:
            return None
        estado_anterior = registro.estado
        update_data = data.model_dump(exclude_unset=True)
        if estado_anterior == 0:
            update_data['estado'] = 1
        for key, value in update_data.items():
            setattr(registro, key, value)
        self.db.commit()
        self.db.refresh(registro)
        accion = "FINALIZADO" if estado_anterior == 0 and registro.estado == 1 else "ACTUALIZADO"
        self.db.add(Historial(
            accion=accion,
            fecha=datetime.now().date(),
            hora=datetime.now().time().replace(microsecond=0),
            usuario_id=usuario_id,
            registro_id=registro.id
        ))
        self.db.commit()
        return registro