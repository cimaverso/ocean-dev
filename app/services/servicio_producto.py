from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
import io
import pandas as pd
from app.models import *
from openpyxl import Workbook
from typing import Optional
from datetime import date
from app.models.registro.producto.modelo_producto import Producto,ProductoCreate, ProductoUpdate


class ProductoService:
    def __init__(self, db: Session):
        self.db = db

    def listar_productos_tipo(self, tipo):
    
        statement = select(Producto).where(Producto.prod_idtipoproducto == tipo).options(
            selectinload(Producto.tipo_producto),  # Cargar relación 'tipo_producto'
            selectinload(Producto.proceso_producto),  # Cargar relación 'proceso_producto'
            selectinload(Producto.unidad_medida)  # Cargar relación 'unidad_medida'
        ).order_by(Producto.prod_id)
        
        results = self.db.exec(statement)
        return results.all()
    
    def listar_producto_id(self, prod_id: int):
        statement = (
            select(Producto)
            .where(Producto.prod_id == prod_id)
            .options(
                selectinload(Producto.tipo_producto),
                selectinload(Producto.proceso_producto),
                selectinload(Producto.unidad_medida)
            )
        )
        result = self.db.exec(statement).first()
        return result
   

    def exportar_productos(self, tipo_producto: int, consulta: Optional[str] = None):
        """Exporta una entidad (producto, servicio) a un archivo Excel filtrado por la consulta proporcionada"""

        # Empezamos con la consulta base, filtrando por tipo de producto
        productos = select(Producto).where(Producto.prod_idtipoproducto == tipo_producto)
        
        # Si hay una consulta, filtramos los productos basados en esta consulta
        if consulta:
            consulta = consulta.lower()
            productos = productos.where(
                Producto.prod_codigo.ilike(f"%{consulta}%") | 
                Producto.prod_nombre.ilike(f"%{consulta}%") |
                Producto.unidad_medida.has(UnidadMedida.um_nombre.ilike(f"%{consulta}%")) |  # Usamos `has()` aquí
                Producto.proceso_producto.has(ProcesoProducto.pp_nombre.ilike(f"%{consulta}%"))  # Usamos `has()` aquí
            )
        
        result = self.db.execute(productos)
        productos = result.scalars().all()  # Utiliza scalars() para obtener las instancias

        # Convertir a DataFrame
        data = [
            {
                "Codigo": producto.prod_codigo, 
                "Producto": producto.prod_nombre, 
                "Unidad Medida": producto.unidad_medida.um_nombre if producto.unidad_medida else 'N/A',
                "Proceso Producto": producto.proceso_producto.pp_nombre if producto.proceso_producto else 'N/A'
            }
            for producto in productos
        ]
        
        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = {1: "Productos", 2: "Servicios",}.get(tipo_producto, "Producto")
            column_name = {1: "Producto", 2: "Servicio"}.get(tipo_producto, "Producto")
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            # Obtener el libro y la hoja activa
            workbook = writer.book
            sheet = workbook[sheet_name]

            sheet.cell(row=1, column=2, value=column_name)  # Cambiar el nombre de la columna

            
            # Ajustar el ancho de las columnas al contenido
            for col in sheet.columns:
                max_length = 0
                column = col[0].column_letter  # Obtiene la letra de la columna
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)  # Añadir espacio extra
                sheet.column_dimensions[column].width = adjusted_width
        
        output.seek(0)

        return output

    def crear_producto(self, producto_data: ProductoCreate):
        nuevo_producto = Producto(**producto_data.dict())

        self.db.add(nuevo_producto)
        self.db.commit()
        self.db.refresh(nuevo_producto)

        statement = select(Producto).options(
            selectinload(Producto.tipo_producto),  # Cargar relación 'tipo_producto'
            selectinload(Producto.proceso_producto),  # Cargar relación 'proceso_producto'
            selectinload(Producto.unidad_medida)  # Cargar relación 'unidad_medida'
        ).where(Producto.prod_id == nuevo_producto.prod_id)

        return self.db.exec(statement).first()

    def actualizar_producto(self, prod_id: int, producto_data: ProductoUpdate):
        statement = select(Producto).where(Producto.prod_id == prod_id)
        producto_db = self.db.exec(statement).first()
        
        if not producto_db:
            return None

        update_data = producto_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(producto_db, key, value)

        self.db.commit()
        self.db.refresh(producto_db)

        return producto_db
    
    def eliminar_producto(self, prod_id: int) -> bool:
        statement = select(Producto).where(Producto.prod_id == prod_id)
        producto_db = self.db.exec(statement).first()
        
        if not producto_db:
            return False
        
        self.db.delete(producto_db)
        self.db.commit()

        return True
