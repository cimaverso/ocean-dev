from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, desc, and_, or_, text, func
from datetime import date, datetime
import pandas as pd
from app.models.registro import Registro
from app.models.historial import Historial
from app.models.vehiculo import Vehiculo
from app.models.conductor import Conductor
from app.models.entidad import Entidad
from app.models.producto import Producto
from app.models.comprador import Comprador
from app.models.transportadora import Transportadora
from app.models.origen import Origen
from app.models.destino import Destino
from app.models.patio import Patio
from app.models.factura import Factura
from app.schemas.registro import RegistroCreate, RegistroUpdate
from typing import Optional
import io


def _load_all(query):
    return query.options(
        selectinload(Registro.tipo),
        selectinload(Registro.vehiculo),
        selectinload(Registro.trailer),
        selectinload(Registro.conductor),
        selectinload(Registro.entidad),
        selectinload(Registro.producto),
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
        workbook = writer.book
        sheet = workbook[sheet_name]
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except Exception:
                    pass
            sheet.column_dimensions[column].width = max_length + 2
    output.seek(0)
    return output


class RegistroService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_registros_transito(self):
        return self.db.execute(
            _load_all(select(Registro))
            .where(Registro.estado == 0)
            .order_by(desc(Registro.fecha_entrada), desc(Registro.hora_entrada))
        ).scalars().all()

    def obtener_registros_historial(self):
        hoy = date.today()
        return self.db.execute(
            _load_all(select(Registro))
            .where(and_(Registro.fecha_salida == hoy, Registro.estado == 1))
            .order_by(desc(Registro.fecha_salida), desc(Registro.hora_salida))
        ).scalars().all()

    def obtener_registros_finalizados(self, tipo: int, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None):
        if not fecha_inicio and not fecha_fin:
            hoy = date.today()
            fecha_inicio = hoy
            fecha_fin = hoy

        return self.db.execute(
            _load_all(select(Registro))
            .where(
                Registro.tipo_id == tipo,
                Registro.estado == 1,
                Registro.fecha_salida >= fecha_inicio,
                Registro.fecha_salida <= fecha_fin
            )
            .order_by(desc(Registro.fecha_salida), desc(Registro.hora_salida))
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
            consulta = consulta.lower()
            query = query.where(or_(
                Registro.origen.has(Origen.nombre.ilike(f"%{consulta}%")),
                Registro.factura.has(Factura.fecha.ilike(f"%{consulta}%")),
                Registro.vehiculo.has(Vehiculo.placa.ilike(f"%{consulta}%")),
                Registro.conductor.has(Conductor.nombre.ilike(f"%{consulta}%")),
                Registro.conductor.has(Conductor.cedula.ilike(f"%{consulta}%")),
                Registro.entidad.has(Entidad.codigo.ilike(f"%{consulta}%")),
                Registro.entidad.has(Entidad.nombre.ilike(f"%{consulta}%")),
                Registro.comprador.has(Comprador.codigo.ilike(f"%{consulta}%")),
                Registro.comprador.has(Comprador.nombre.ilike(f"%{consulta}%")),
                Registro.producto.has(Producto.codigo.ilike(f"%{consulta}%")),
                Registro.producto.has(Producto.nombre.ilike(f"%{consulta}%")),
                Registro.patio.has(Patio.nombre.ilike(f"%{consulta}%")),
                Registro.observaciones.ilike(f"%{consulta}%")
            ))

        ingresos = self.db.execute(query).scalars().all()

        data = [{
            'Tiquete': r.tiquete,
            'Registro': r.consecutivo,
            'Tipo': r.tipo.nombre,
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
            'Observaciones': r.observaciones,
        } for r in ingresos]

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
            consulta = consulta.lower()
            query = query.where(or_(
                Registro.vehiculo.has(Vehiculo.placa.ilike(f"%{consulta}%")),
                Registro.conductor.has(Conductor.nombre.ilike(f"%{consulta}%")),
                Registro.conductor.has(Conductor.cedula.ilike(f"%{consulta}%")),
                Registro.entidad.has(Entidad.codigo.ilike(f"%{consulta}%")),
                Registro.entidad.has(Entidad.nombre.ilike(f"%{consulta}%")),
                Registro.destino.has(Destino.nombre.ilike(f"%{consulta}%")),
                Registro.producto.has(Producto.codigo.ilike(f"%{consulta}%")),
                Registro.producto.has(Producto.nombre.ilike(f"%{consulta}%")),
                Registro.patio.has(Patio.nombre.ilike(f"%{consulta}%")),
                Registro.transportadora.has(Transportadora.nombre.ilike(f"%{consulta}%")),
                Registro.orden.ilike(f"%{consulta}%"),
                Registro.precinto.ilike(f"%{consulta}%"),
                Registro.observaciones.ilike(f"%{consulta}%")
            ))

        despachos = self.db.execute(query).scalars().all()

        data = [{
            'Tiquete': r.tiquete,
            'Registro': r.consecutivo,
            'Tipo': r.tipo.nombre,
            'Fecha Entrada': r.fecha_entrada.strftime("%Y-%m-%d") if r.fecha_entrada else '',
            'Hora Entrada': r.hora_entrada.strftime("%I:%M %p") if r.hora_entrada else '',
            'Fecha Salida': r.fecha_salida.strftime("%Y-%m-%d") if r.fecha_salida else '',
            'Hora Salida': r.hora_salida.strftime("%I:%M %p") if r.hora_salida else '',
            'Placa': r.vehiculo.placa if r.vehiculo else None,
            'Trailer': r.trailer.placa if r.trailer else None,
            'Conductor': r.conductor.nombre if r.conductor else None,
            'Cedula Conductor': r.conductor.cedula if r.conductor else None,
            'Codigo Cliente': r.entidad.codigo if r.entidad else None,
            'Cliente': r.entidad.nombre if r.entidad else None,
            'Codigo Destino': r.destino.codigo if r.destino else None,
            'Destino': r.destino.nombre if r.destino else None,
            'Codigo Producto': r.producto.codigo if r.producto else None,
            'Producto': r.producto.nombre if r.producto else None,
            'Peso Bruto': int(r.peso_bruto) if r.peso_bruto else None,
            'Peso Tara': int(r.peso_tara) if r.peso_tara else None,
            'Peso Neto': int(r.peso_neto) if r.peso_neto else None,
            'Origen': r.origen.nombre if r.origen else None,
            'Patio': r.patio.nombre if r.patio else None,
            'Transportadora': r.transportadora.nombre if r.transportadora else None,
            'Orden': r.orden,
            'Precinto': r.precinto,
            'Observaciones': r.observaciones,
        } for r in despachos]

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
            consulta = consulta.lower()
            query = query.where(or_(
                Registro.vehiculo.has(Vehiculo.placa.ilike(f"%{consulta}%")),
                Registro.conductor.has(Conductor.nombre.ilike(f"%{consulta}%")),
                Registro.conductor.has(Conductor.cedula.ilike(f"%{consulta}%")),
                Registro.entidad.has(Entidad.codigo.ilike(f"%{consulta}%")),
                Registro.entidad.has(Entidad.nombre.ilike(f"%{consulta}%")),
                Registro.destino.has(Destino.nombre.ilike(f"%{consulta}%")),
                Registro.producto.has(Producto.codigo.ilike(f"%{consulta}%")),
                Registro.producto.has(Producto.nombre.ilike(f"%{consulta}%")),
                Registro.patio.has(Patio.nombre.ilike(f"%{consulta}%")),
                Registro.transportadora.has(Transportadora.nombre.ilike(f"%{consulta}%")),
                Registro.orden.ilike(f"%{consulta}%"),
                Registro.precinto.ilike(f"%{consulta}%"),
                Registro.observaciones.ilike(f"%{consulta}%")
            ))

        servicios = self.db.execute(query).scalars().all()

        data = [{
            'Tiquete': r.tiquete,
            'Registro': r.consecutivo,
            'Tipo': r.tipo.nombre,
            'Fecha Entrada': r.fecha_entrada.strftime("%Y-%m-%d") if r.fecha_entrada else '',
            'Hora Entrada': r.hora_entrada.strftime("%I:%M %p") if r.hora_entrada else '',
            'Fecha Salida': r.fecha_salida.strftime("%Y-%m-%d") if r.fecha_salida else '',
            'Hora Salida': r.hora_salida.strftime("%I:%M %p") if r.hora_salida else '',
            'Placa': r.vehiculo.placa if r.vehiculo else None,
            'Trailer': r.trailer.placa if r.trailer else None,
            'Conductor': r.conductor.nombre if r.conductor else None,
            'Cedula Conductor': r.conductor.cedula if r.conductor else None,
            'Codigo Tercero': r.entidad.codigo if r.entidad else None,
            'Tercero': r.entidad.nombre if r.entidad else None,
            'Codigo Comprador': r.comprador.codigo if r.comprador else None,
            'Comprador': r.comprador.nombre if r.comprador else None,
            'Codigo Producto': r.producto.codigo if r.producto else None,
            'Producto': r.producto.nombre if r.producto else None,
            'Peso Bruto': int(r.peso_bruto) if r.peso_bruto else None,
            'Peso Tara': int(r.peso_tara) if r.peso_tara else None,
            'Peso Neto': int(r.peso_neto) if r.peso_neto else None,
            'Origen': r.origen.nombre if r.origen else None,
            'Patio': r.patio.nombre if r.patio else None,
            'Unidad': r.producto.unidad_medida.nombre if r.producto and r.producto.unidad_medida else None,
            'Cantidad': r.cantidad,
            'Observaciones': r.observaciones,
        } for r in servicios]

        return _excel_output(pd.DataFrame(data), "Servicios")

    def calcular_ingresos(self):
        hoy = date.today()

        total = self.db.execute(
            select(func.sum(Registro.peso_neto)).where(
                Registro.tipo_id == 1, Registro.fecha_salida == hoy
            )
        ).scalar() or 0

        registros = self.db.execute(
            select(Registro).options(selectinload(Registro.producto)).where(
                Registro.tipo_id == 1, Registro.fecha_salida == hoy
            )
        ).scalars().all()

        pesos_por_producto = {}
        for r in registros:
            if r.producto:
                nombre = r.producto.nombre
                pesos_por_producto[nombre] = pesos_por_producto.get(nombre, 0) + (r.peso_neto or 0)

        return {
            "total_peso_neto": f"{total / 1000:,.3f}",
            "productos": {n: {"peso_neto_producto": f"{p / 1000:,.3f}"} for n, p in pesos_por_producto.items()}
        }

    def calcular_despachos(self):
        hoy = date.today()

        total = self.db.execute(
            select(func.sum(Registro.peso_neto)).where(
                Registro.tipo_id == 2, Registro.fecha_salida == hoy
            )
        ).scalar() or 0

        registros = self.db.execute(
            select(Registro).options(selectinload(Registro.destino)).where(
                Registro.tipo_id == 2, Registro.fecha_salida == hoy
            )
        ).scalars().all()

        pesos_por_destino = {}
        for r in registros:
            if r.destino:
                nombre = r.destino.nombre
                pesos_por_destino[nombre] = pesos_por_destino.get(nombre, 0) + (r.peso_neto or 0)

        return {
            "total_peso_neto": f"{total / 1000:,.3f}",
            "destinos": {n: {"peso_neto_destino": f"{p / 1000:,.3f}"} for n, p in pesos_por_destino.items()}
        }

    def obtener_consecutivo(self):
        return self.db.execute(text("SELECT nextval('reg_consecutivo_seq')")).scalar()

    def obtener_consecutivo_tiquete(self):
        return self.db.execute(text("SELECT nextval('reg_tiquete_seq')")).scalar()

    def crear_registro(self, registro_data: RegistroCreate, usuario_id: int):
        data_dict = registro_data.model_dump()
        data_dict['estado'] = 0
        nuevo_registro = Registro(**data_dict)

        self.db.add(nuevo_registro)
        self.db.commit()
        self.db.refresh(nuevo_registro)

        self.db.add(Historial(
            accion="CREADO",
            fecha=datetime.now().date(),
            hora=datetime.now().time().replace(microsecond=0),
            usuario_id=usuario_id,
            registro_id=nuevo_registro.id
        ))
        self.db.commit()

        return nuevo_registro

    def actualizar_registro(self, id: int, registro_data: RegistroUpdate, usuario_id: int):
        registro_db = self.db.execute(
            select(Registro).where(Registro.id == id)
        ).scalar_one_or_none()

        if not registro_db:
            return None

        estado_anterior = registro_db.estado
        update_data = registro_data.model_dump(exclude_unset=True)

        if estado_anterior == 0:
            update_data['estado'] = 1

        for key, value in update_data.items():
            setattr(registro_db, key, value)

        self.db.commit()
        self.db.refresh(registro_db)

        accion = "FINALIZADO" if estado_anterior == 0 and registro_db.estado == 1 else "ACTUALIZADO"

        self.db.add(Historial(
            accion=accion,
            fecha=datetime.now().date(),
            hora=datetime.now().time().replace(microsecond=0),
            usuario_id=usuario_id,
            registro_id=registro_db.id
        ))
        self.db.commit()

        return registro_db