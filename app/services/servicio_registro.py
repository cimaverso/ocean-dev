from sqlmodel import Session, select, desc, and_, or_, text, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from datetime import date, datetime
import pandas as pd
from app.models import *
from typing import Optional
from datetime import date
from app.models.registro.modelo_registro import Registro, RegistroCreate, RegistroUpdate
from jinja2 import Environment, FileSystemLoader, select_autoescape
import io
import os
from weasyprint import HTML
import base64


class RegistroService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_registros_transito(self):
        registros = (
            select(Registro).options(
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
                selectinload(Registro.tipo),
            ).where(Registro.reg_estado == 0)
            .order_by(
                desc(Registro.reg_fechaentrada), 
                desc(Registro.reg_horaentrada)
            )
        )
        results = self.db.exec(registros)
        return results.all()
    
    def obtener_registros_historial(self):
        fecha_actual = date.today()
        
        query = (
            select(Registro)
            .options(
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
                selectinload(Registro.tipo),
            )
            .where(
                and_(
                    Registro.reg_fechasalida == fecha_actual,
                    Registro.reg_estado == 1
                )
            )
            .order_by(
                desc(Registro.reg_fechasalida),
                desc(Registro.reg_horasalida)
            )
        )

        results = self.db.exec(query)
        return results.all()

    def obtener_registros_finalizados(
        self, tipo: int, fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ):
        if not fecha_inicio and not fecha_fin:
            today = date.today()
            fecha_inicio = today
            fecha_fin = today

        query = (
            select(Registro)
            .options(
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
            .where(
                Registro.reg_idtipo == tipo,
                Registro.reg_estado == 1,
                Registro.reg_fechasalida >= fecha_inicio,
                Registro.reg_fechasalida <= fecha_fin
            )
            .order_by(
                Registro.reg_fechasalida.desc(),
                Registro.reg_horasalida.desc()
            )
            
        )

        results = self.db.exec(query).yield_per(500)
        return results.all()

    def abrir_registro(self, registro_id: int):
        # Obtener el registro por su ID
        statement = select(Registro).where(Registro.reg_id == registro_id)
        registro = self.db.exec(statement).first()

        if not registro:
            return None
        
        if registro.reg_acceso == 1:
            raise HTTPException(status_code=400, detail="El registro ya esta abierto por otro usuario")

        # Marcar como "en uso"
        registro.reg_acceso = 1
        self.db.add(registro)
        self.db.commit()  # Hacemos commit en la base de datos

        return registro
    
    def cerrar_registro(self, registro_id: int):
        # Obtener el registro por su ID
        statement = select(Registro).where(Registro.reg_id == registro_id)
        registro = self.db.exec(statement).first()

        if not registro:
            return None
        
        if registro.reg_acceso == 0:
            raise HTTPException(status_code=200, detail="El registro ya esta cerrado")
        
        # Marcar como "sin uso"
        registro.reg_acceso = 0
        self.db.add(registro)
        self.db.commit()  # Hacemos commit en la base de datos

        return registro

    def exportar_ingreso(self, consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None):
        print(f"Consulta recibida: {consulta}")
        
        ingresos = select(Registro).where(
            Registro.reg_idtipo == 1,
            Registro.reg_estado == 1
        )
        
        #filtro de fechas

        if fecha_inicio and fecha_fin:
            ingresos = ingresos.where(Registro.reg_fechasalida.between(fecha_inicio, fecha_fin))
        elif fecha_inicio:
            ingresos = ingresos.where(Registro.reg_fechasalida >= fecha_inicio)
        elif fecha_fin:
            ingresos = ingresos.where(Registro.reg_fechasalida <= fecha_fin)
       


        if consulta:
            consulta = consulta.lower()
            ingresos = ingresos.where(
                or_(
                    Registro.origen.has(Origen.ori_nombre.ilike(f"%{consulta}%")),
                    Registro.factura.has(Factura.fac_fecha.ilike(f"%{consulta}%")),
                    Registro.vehiculo.has(Vehiculo.vehi_placa.ilike(f"%{consulta}%")),
                    Registro.conductor.has(Conductor.conduct_nombre.ilike(f"%{consulta}%")),
                    Registro.conductor.has(Conductor.conduct_cedula.ilike(f"%{consulta}%")),
                    Registro.entidad.has(Entidad.ent_codigo.ilike(f"%{consulta}%")),
                    Registro.entidad.has(Entidad.ent_nombre.ilike(f"%{consulta}%")),
                    Registro.comprador.has(Comprador.comp_codigo.ilike(f"%{consulta}%")),
                    Registro.comprador.has(Comprador.comp_nombre.ilike(f"%{consulta}%")),
                    Registro.producto.has(Producto.prod_codigo.ilike(f"%{consulta}%")),
                    Registro.producto.has(Producto.prod_nombre.ilike(f"%{consulta}%")),
                    Registro.patio.has(Patio.pat_nombre.ilike(f"%{consulta}%")),
                    Registro.reg_observaciones.ilike(f"%{consulta}%")
                )
            )

        result = self.db.execute(ingresos)
        ingresos = result.scalars().all()  # Esto obtiene los registros reales

        data = [
            {
                'Tiquete': ingreso.reg_tiquete,
                'Registro': ingreso.reg_consecutivo,
                'Tipo': ingreso.tipo.tr_nombre,
                'Facturado': ingreso.factura.fac_fecha if ingreso.factura else None,
                'Origen': ingreso.origen.ori_nombre if ingreso.origen else None,
                'Fecha Entrada': ingreso.reg_fechaentrada.strftime("%Y-%m-%d") if ingreso.reg_fechaentrada else '',
                'Hora Entrada': ingreso.reg_horaentrada.strftime("%I:%M %p") if ingreso.reg_horaentrada else '',
                'Fecha Salida': ingreso.reg_fechasalida.strftime("%Y-%m-%d") if ingreso.reg_fechasalida else '',
                'Hora Salida': ingreso.reg_horasalida.strftime("%I:%M %p") if ingreso.reg_horasalida else '',
                'Placa': ingreso.vehiculo.vehi_placa if ingreso.vehiculo else None,
                'Trailer': ingreso.trailer.trai_placa if ingreso.trailer else None,
                'Conductor': ingreso.conductor.conduct_nombre if ingreso.conductor else None,
                'Cedula Conductor': ingreso.conductor.conduct_cedula if ingreso.conductor else None,
                'Codigo Proveedor': ingreso.entidad.ent_codigo if ingreso.entidad else None,
                'Proveedor': ingreso.entidad.ent_nombre if ingreso.entidad else None,
                'Codigo Comprador': ingreso.comprador.comp_codigo if ingreso.comprador else None,
                'Comprador': ingreso.comprador.comp_nombre if ingreso.comprador else None,
                'Codigo Producto': ingreso.producto.prod_codigo if ingreso.producto else None,
                'Producto': ingreso.producto.prod_nombre if ingreso.producto else None,
                'Peso Bruto': int(ingreso.reg_pesobruto) if ingreso.reg_pesobruto else None,
                'Peso Tara': int(ingreso.reg_pesotara) if ingreso.reg_pesotara else None,
                'Peso Neto': int(ingreso.reg_pesoneto) if ingreso.reg_pesoneto else None,
                'Patio': ingreso.patio.pat_nombre if ingreso.patio else None,
                'Observaciones': ingreso.reg_observaciones if ingreso.reg_observaciones else None,
            }
            for ingreso in ingresos
        ]

        # Crear DataFrame
        df = pd.DataFrame(data)

        # Crear Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Ingresos")
            workbook = writer.book
            sheet = workbook["Ingresos"]

            # Ajustar el ancho de columnas
            for col in sheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                sheet.column_dimensions[column].width = max_length + 2

        output.seek(0)
        return output

    def exportar_despacho(self, consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None):
        # Construir la consulta base
        despachos = select(Registro).where(
            Registro.reg_idtipo == 2, 
            Registro.reg_estado == 1
        )

        # Aplicar filtro de fechas si se proporcionan
        if fecha_inicio and fecha_fin:
            despachos = despachos.where(Registro.reg_fechaentrada.between(fecha_inicio, fecha_fin))
        elif fecha_inicio:
            despachos = despachos.where(Registro.reg_fechaentrada >= fecha_inicio)
        elif fecha_fin:
            despachos = despachos.where(Registro.reg_fechaentrada <= fecha_fin)

        # Aplicar filtro de búsqueda si se proporciona
        if consulta:
            consulta = consulta.lower()
            despachos = despachos.where(
                (Registro.vehiculo.has(Vehiculo.vehi_placa.ilike(f"%{consulta}%"))) |
                (Registro.conductor.has(Conductor.conduct_nombre.ilike(f"%{consulta}%"))) |
                (Registro.conductor.has(Conductor.conduct_cedula.ilike(f"%{consulta}%"))) |
                (Registro.entidad.has(Entidad.ent_codigo.ilike(f"%{consulta}%"))) |
                (Registro.entidad.has(Entidad.ent_nombre.ilike(f"%{consulta}%"))) |
                (Registro.destino.has(Destino.dest_nombre.ilike(f"%{consulta}%"))) |
                (Registro.producto.has(Producto.prod_codigo.ilike(f"%{consulta}%"))) |
                (Registro.producto.has(Producto.prod_nombre.ilike(f"%{consulta}%"))) |
                (Registro.patio.has(Patio.pat_nombre.ilike(f"%{consulta}%"))) |
                (Registro.transportadora.has(Transportadora.trans_nombre.ilike(f"%{consulta}%"))) |
                (Registro.reg_orden.ilike(f"%{consulta}%")) |
                (Registro.reg_precinto.ilike(f"%{consulta}%")) |
                (Registro.reg_observaciones.ilike(f"%{consulta}%"))
            )

        # Ejecutar la consulta para obtener los resultados
        result = self.db.execute(despachos)
        despachos = result.scalars().all()  # Esto obtiene los registros reales

        # Crear una lista con los datos de los despachos
        data = [
            {
                'Tiquete': despacho.reg_tiquete,
                'Registro': despacho.reg_consecutivo,
                'Tipo': despacho.tipo.tr_nombre,
                'Fecha Entrada': despacho.reg_fechaentrada.strftime("%Y-%m-%d") if despacho.reg_fechaentrada else '',
                'Hora Entrada': despacho.reg_horaentrada.strftime("%I:%M %p") if despacho.reg_horaentrada else '',
                'Fecha Salida': despacho.reg_fechasalida.strftime("%Y-%m-%d") if despacho.reg_fechasalida else '',
                'Hora Salida': despacho.reg_horasalida.strftime("%I:%M %p") if despacho.reg_horasalida else '',
                'Placa': despacho.vehiculo.vehi_placa if despacho.vehiculo else None,
                'Trailer': despacho.trailer.trai_placa if despacho.trailer else None,
                'Conductor': despacho.conductor.conduct_nombre if despacho.conductor else None,
                'Cedula Conductor': despacho.conductor.conduct_cedula if despacho.conductor else None,
                'Codigo Cliente': despacho.entidad.ent_codigo if despacho.entidad else None,
                'Cliente': despacho.entidad.ent_nombre if despacho.entidad else None,
                'Codigo Destino': despacho.destino.dest_codigo if despacho.destino else None,
                'Destino': despacho.destino.dest_nombre if despacho.destino else None,
                'Codigo Producto': despacho.producto.prod_codigo if despacho.producto else None,
                'Producto': despacho.producto.prod_nombre if despacho.producto else None,
                'Peso Bruto': int(despacho.reg_pesobruto) if despacho.reg_pesobruto else None,
                'Peso Tara': int(despacho.reg_pesotara) if despacho.reg_pesotara else None,
                'Peso Neto': int(despacho.reg_pesoneto) if despacho.reg_pesoneto else None,
                'Origen': despacho.origen.ori_nombre if despacho.origen else None,
                'Patio': despacho.patio.pat_nombre if despacho.patio else None, 
                'Transportadora': despacho.transportadora.trans_nombre if despacho.transportadora else None,
                'Orden': despacho.reg_orden if despacho.reg_orden else None,
                'Precinto': despacho.reg_precinto if despacho.reg_precinto else None,
                'Observaciones': despacho.reg_observaciones if despacho.reg_observaciones else None, 
            }
            for despacho in despachos
        ]

        # Convertir los datos a un DataFrame
        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Despachos")
            workbook = writer.book
            sheet = workbook["Despachos"]
            
            # Ajustar el ancho de las columnas al contenido
            for col in sheet.columns:
                max_length = 0
                column = col[0].column_letter  # Obtener la letra de la columna
                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                sheet.column_dimensions[column].width = max_length + 2

        output.seek(0)
        return output

    def exportar_servicio(self, consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None):
        servicios = select(Registro).where(
            Registro.reg_idtipo == 3,
            Registro.reg_estado == 1
        )

        
        # Aplicar filtro de fechas si se proporcionan
        if fecha_inicio and fecha_fin:
            servicios = servicios.where(Registro.reg_fechaentrada.between(fecha_inicio, fecha_fin))
        elif fecha_inicio:
            servicios = servicios.where(Registro.reg_fechaentrada >= fecha_inicio)
        elif fecha_fin:
            servicios = servicios.where(Registro.reg_fechaentrada <= fecha_fin)
        
        
        # Aplicar filtro de búsqueda si se proporciona
        if consulta:
            consulta = consulta.lower()
            servicios = servicios.where(
                (Registro.vehiculo.has(Vehiculo.vehi_placa.ilike(f"%{consulta}%"))) |
                (Registro.conductor.has(Conductor.conduct_nombre.ilike(f"%{consulta}%"))) |
                (Registro.conductor.has(Conductor.conduct_cedula.ilike(f"%{consulta}%"))) |
                (Registro.entidad.has(Entidad.ent_codigo.ilike(f"%{consulta}%"))) |
                (Registro.entidad.has(Entidad.ent_nombre.ilike(f"%{consulta}%"))) |
                (Registro.destino.has(Destino.dest_nombre.ilike(f"%{consulta}%"))) |
                (Registro.productos.has(Producto.prod_codigo.ilike(f"%{consulta}%"))) |
                (Registro.productos.has(Producto.prod_nombre.ilike(f"%{consulta}%"))) |
                (Registro.patio.has(Patio.pat_nombre.ilike(f"%{consulta}%"))) |
                (Registro.transportadora.has(Transportadora.trans_nombre.ilike(f"%{consulta}%"))) |
                (Registro.reg_orden.ilike(f"%{consulta}%")) |
                (Registro.reg_precinto.ilike(f"%{consulta}%")) |
                (Registro.reg_observaciones.ilike(f"%{consulta}%"))
            )
        
        # Ejecutar la consulta para obtener los resultados
        result = self.db.execute(servicios)
        servicios = result.scalars().all()  # Esto obtiene los registros reales

        data = [
            { 
                'Tiquete': servicio.reg_tiquete,
                'Registro': servicio.reg_consecutivo,
                'Tipo': servicio.tipo.tr_nombre,
                'Fecha Entrada': servicio.reg_fechaentrada.strftime("%Y-%m-%d") if servicio.reg_fechaentrada else '',
                'Hora Entrada': servicio.reg_horaentrada.strftime("%I:%M %p") if servicio.reg_horaentrada else '',
                'Fecha Salida': servicio.reg_fechasalida.strftime("%Y-%m-%d") if servicio.reg_fechasalida else '',
                'Hora Salida': servicio.reg_horasalida.strftime("%I:%M %p") if servicio.reg_horasalida else '',
                'Placa': servicio.vehiculo.vehi_placa if servicio.vehiculo and servicio.vehiculo else None,
                'Trailer': servicio.trailer.trai_placa if servicio.trailer and servicio.trailer else None,
                'Conductor': servicio.conductor.conduct_nombre if servicio.conductor else None,
                'Cedula Conductor': servicio.conductor.conduct_cedula if servicio.conductor else None,
                'Codigo Tercero': servicio.entidad.ent_codigo if servicio.entidad else None,
                'Tercero': servicio.entidad.ent_nombre if servicio.entidad else None,
                'Codigo Comprador': servicio.comprador.comp_codigo if servicio.comprador else None,
                'Comprador': servicio.comprador.comp_nombre if servicio.comprador else None,
                'Codigo Producto': servicio.producto.prod_codigo if servicio.producto else None,
                'Producto': servicio.producto.prod_nombre if servicio.producto else None,
                'Peso Bruto': int(servicio.reg_pesobruto) if servicio.reg_pesobruto else None,
                'Peso Tara': int(servicio.reg_pesotara) if servicio.reg_pesotara else None,
                'Peso Neto': int(servicio.reg_pesoneto) if servicio.reg_pesoneto else None,
                'Origen': servicio.origen.ori_nombre if servicio.origen else None,
                'Patio': servicio.patio.pat_nombre if servicio.patio else None, 
                'Unidad': servicio.producto.unidad_medida.um_nombre if servicio.producto.unidad_medida else None,  
                'Cantidad': servicio.reg_cantidad if servicio.reg_cantidad else None,  
                'Observaciones': servicio.reg_observaciones if servicio.reg_observaciones else None, 
            }
            for servicio in servicios
        ]


        
        # Convertir datos a DataFrame
        df = pd.DataFrame(data)
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Servicios")
            workbook = writer.book
            sheet = workbook["Servicios"]
            
            # Ajustar el ancho de las columnas al contenido
            for col in sheet.columns:
                max_length = 0
                column = col[0].column_letter  # Obtener la letra de la columna
                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                sheet.column_dimensions[column].width = max_length + 2
        
        output.seek(0)
        return output

    def imprimir_registro(self, registro_id: int, usuario_nombre: str):
        statement = select(Registro).where(Registro.reg_id == registro_id)
        registro = self.db.exec(statement).first()
        if not registro:
            return None
        
        # Formatear valores
        def format_miles(value):
            if value is None:
                return "0"
            value_miles = float(value) / 1000
            return f"{value_miles:,.3f}"
        
        img_path = os.path.join(os.path.dirname(__file__), "..", "static", "Logo.png")

        # Leer y codificar la imagen como base64
        with open(img_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
            encoded_image = f"data:image/png;base64,{encoded_image}"

        # Datos que vas a pasar a la plantilla
        data = {
            'consecutivo': registro.reg_consecutivo,
            'consecutivo_tiquete': registro.reg_tiquete,
            'fecha_entrada': registro.reg_fechaentrada.strftime('%d/%b/%Y'),
            'hora_entrada': registro.reg_horaentrada.strftime('%H:%M'),
            'fecha_salida': registro.reg_fechaentrada.strftime('%d/%b/%Y'),
            'hora_salida': registro.reg_horasalida.strftime('%H:%M'),
            'vehiculo': registro.vehiculo.vehi_placa if registro.vehiculo else '',
            'trailer': registro.trailer.trai_placa if registro.trailer else '',
            'conductor': registro.conductor.conduct_nombre if registro.conductor else '',
            'conductor_cedula': registro.conductor.conduct_cedula if registro.conductor else '',
            'producto': registro.producto.prod_nombre if registro.producto else '',
            'producto_codigo': registro.producto.prod_codigo if registro.producto else '',
            'unidad': registro.producto.unidad_medida.um_nombre if registro.producto and registro.producto.unidad_medida else '',
            'cantidad': format_miles(registro.reg_cantidad) if registro.reg_cantidad else '',
            'origen': registro.origen.ori_nombre if registro.origen else '',
            'destino': registro.destino.dest_nombre if registro.destino else '',
            'destino_codigo': registro.destino.dest_codigo if registro.destino else '',
            'patio': registro.patio.pat_nombre if registro.patio else '',
            'transportadora': registro.transportadora.trans_nombre if registro.transportadora else '',
            'orden': registro.reg_orden if registro.reg_orden else '',
            'precinto': registro.reg_precinto if registro.reg_precinto else '',
            'entidad': registro.entidad.ent_nombre if registro.entidad else '',
            'entidad_codigo': registro.entidad.ent_codigo if registro.entidad else '',
            'comprador': registro.comprador.comp_nombre if registro.comprador else '',
            'comprador_codigo': registro.comprador.comp_codigo if registro.comprador else '',
            'peso_bruto': format_miles(registro.reg_pesobruto),
            'peso_tara': format_miles(registro.reg_pesotara),
            'peso_neto': format_miles(registro.reg_pesoneto),
            'observaciones': registro.reg_observaciones if registro.reg_observaciones else '',
            'username': usuario_nombre,
            'encoded_image': encoded_image
        }

        # Determinar la plantilla según el tipo de registro
        if registro.reg_idtipo == 1:
            template_name = 'registro_ingreso.html'
        elif registro.reg_idtipo == 2:
            template_name = 'registro_despacho.html'
        else:
            template_name = 'registro_servicios.html'  

        # Renderizar plantilla con Jinja2
        template_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), '../templates')),
            autoescape=select_autoescape(['html'])
        )
        template = template_env.get_template(template_name)
        html = template.render(**data)


        pdf = HTML(string=html).write_pdf()

      
        return pdf
    
    def calcular_ingresos(self):
        statement = select(Registro).where(Registro.reg_estado == 1)
        registros = self.db.exec(statement).all()

        if not registros:
            return None

        hoy = date.today()

        # Sumar el peso neto total de registros tipo INGRESO finalizados hoy
        total_peso_neto_query = select(func.sum(Registro.reg_pesoneto)).where(
            Registro.reg_idtipo == 1,
            Registro.reg_fechasalida == hoy
        )
        total_peso_neto_result = self.db.exec(total_peso_neto_query).first()
        total_peso_neto = total_peso_neto_result if total_peso_neto_result is not None else 0

        # Obtener registros de tipo INGRESO finalizados hoy con producto
        registros_query = select(Registro).options(
            selectinload(Registro.producto)
        ).where(
            Registro.reg_idtipo == 1,
            Registro.reg_fechasalida == hoy
        )
        registros = self.db.exec(registros_query).all()

        # Agrupar peso neto por producto
        pesos_por_producto = {}
        for registro in registros:
            nombre_producto = registro.producto.prod_nombre
            peso = registro.reg_pesoneto or 0

            if nombre_producto not in pesos_por_producto:
                pesos_por_producto[nombre_producto] = 0
            pesos_por_producto[nombre_producto] += peso



        resultados = {
            "total_peso_neto": f"{total_peso_neto / 1000:,.3f}",
            "productos": {
                nombre: {
                    "peso_neto_producto": f"{peso / 1000:,.3f}"
                }
                for nombre, peso in pesos_por_producto.items()
            }
        }

        return resultados

    def calcular_despachos(self):
        # Verificar si hay registros activos
        statement = select(Registro).where(Registro.reg_estado == 1)
        registros = self.db.exec(statement).all()

        if not registros:
            return None

        hoy = date.today()

        # Sumar el peso neto total de los registros tipo DESPACHO finalizados hoy
        total_peso_neto_query = select(func.sum(Registro.reg_pesoneto)).where(
            Registro.reg_idtipo == 2,
            Registro.reg_fechasalida == hoy
        )
        total_peso_neto_result = self.db.exec(total_peso_neto_query).first()
        total_peso_neto = total_peso_neto_result if total_peso_neto_result is not None else 0

        # Obtener registros tipo DESPACHO finalizados hoy con relación destino
        registros_query = select(Registro).options(
            selectinload(Registro.destino)
        ).where(
            Registro.reg_idtipo == 2,
            Registro.reg_fechasalida == hoy
        )
        registros = self.db.exec(registros_query).all()

        # Acumular pesos netos por destino
        pesos_por_destino = {}
        for registro in registros:
            if registro.destino:  # Asegura que el destino esté cargado
                nombre_destino = registro.destino.dest_nombre
                peso = registro.reg_pesoneto or 0

                if nombre_destino not in pesos_por_destino:
                    pesos_por_destino[nombre_destino] = 0
                pesos_por_destino[nombre_destino] += peso

        # Formatear resultados
        resultados = {
            "total_peso_neto": f"{total_peso_neto / 1000:,.3f}",  # Total en toneladas
            "destinos": {
                nombre: {
                    "peso_neto_destino": f"{peso / 1000:,.3f}"
                }
                for nombre, peso in pesos_por_destino.items()
            }
        }

        return resultados

    def obtener_consecutivo(self):
        consecutivo = self.db.exec(text("SELECT nextval('reg_consecutivo_seq')")).scalar()
        return consecutivo
    
    def obtener_consecutivo_tiquete(self):
        tiquete = self.db.exec(text("SELECT nextval('reg_tiquete_seq')")).scalar()
        return tiquete

    def crear_registro(self, registro_data: RegistroCreate, usuario_id: int):
        
        data_dict = registro_data.dict()
        data_dict['reg_estado'] = 0
      
        nuevo_registro = Registro(**data_dict)

        self.db.add(nuevo_registro)
        self.db.commit()  # Guardar el registro en la DB
        self.db.refresh(nuevo_registro)  # Refrescar para obtener los datos actualizados

        # Crear la entrada en la tabla de Historial
        nuevo_historial = Historial(
            his_accion="CREADO",  # Acción que se está realizando
            his_fecha=datetime.now().date(),  # Fecha actual
            his_hora=datetime.now().time().replace(microsecond=0), # Hora actual
            his_idusuario=usuario_id,  # ID del usuario (debes pasar el usuario que está creando el registro)
            his_idregistro=nuevo_registro.reg_id  # ID del nuevo registro creado
        )

        # Añadir el historial a la base de datos
        self.db.add(nuevo_historial)
        self.db.commit()  # Guardar el historial
        self.db.refresh(nuevo_historial)  # Refrescar para obtener los datos actualizados

        return nuevo_registro
    
    def actualizar_registro(self, reg_id: int, registro_data: RegistroUpdate, usuario_id: int):
        statement = select(Registro).where(Registro.reg_id == reg_id)
        registro_db = self.db.exec(statement).first()

        if not registro_db:
            return None  # Si el registro no existe, devolvemos None

        estado_anterior = registro_db.reg_estado  # Guardamos el estado original
        update_data = registro_data.dict(exclude_unset=True)

        # Solo actualizar a 1 si no está ya finalizado
        if estado_anterior == 0:
            update_data['reg_estado'] = 1

        for key, value in update_data.items():
            setattr(registro_db, key, value)

        self.db.commit()
        self.db.refresh(registro_db)

        # Determinar la acción para historial
        if estado_anterior == 0 and registro_db.reg_estado == 1:
            accion = "FINALIZADO"
        else:
            accion = "ACTUALIZADO"

        nuevo_historial = Historial(
            his_accion=accion,
            his_fecha=datetime.now().date(),
            his_hora=datetime.now().time().replace(microsecond=0),
            his_idusuario=usuario_id,
            his_idregistro=registro_db.reg_id
        )

        self.db.add(nuevo_historial)
        self.db.commit()
        self.db.refresh(nuevo_historial)

        return registro_db





    

    



        





