from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.models.producto import Producto
from app.models.unidad_medida import UnidadMedida
from app.models.proceso_producto import ProcesoProducto
from app.schemas.producto import ProductoCreate, ProductoUpdate
from typing import Optional
import pandas as pd
import io


class ProductoService:
    def __init__(self, db: Session):
        self.db = db

    def listar_productos_tipo(self, tipo: int):
        return self.db.execute(
            select(Producto)
            .where(Producto.tipo_producto_id == tipo)
            .options(
                selectinload(Producto.tipo_producto),
                selectinload(Producto.proceso_producto),
                selectinload(Producto.unidad_medida)
            )
            .order_by(Producto.id)
        ).scalars().all()

    def listar_producto_id(self, id: int):
        return self.db.execute(
            select(Producto)
            .where(Producto.id == id)
            .options(
                selectinload(Producto.tipo_producto),
                selectinload(Producto.proceso_producto),
                selectinload(Producto.unidad_medida)
            )
        ).scalar_one_or_none()

    def exportar_productos(self, tipo_producto: int, consulta: Optional[str] = None):
        query = select(Producto).where(Producto.tipo_producto_id == tipo_producto)

        if consulta:
            consulta = consulta.lower()
            query = query.where(
                Producto.codigo.ilike(f"%{consulta}%") |
                Producto.nombre.ilike(f"%{consulta}%") |
                Producto.unidad_medida.has(UnidadMedida.nombre.ilike(f"%{consulta}%")) |
                Producto.proceso_producto.has(ProcesoProducto.nombre.ilike(f"%{consulta}%"))
            )

        productos = self.db.execute(query).scalars().all()

        data = [
            {
                "Codigo": p.codigo,
                "Producto": p.nombre,
                "Unidad Medida": p.unidad_medida.nombre if p.unidad_medida else "N/A",
                "Proceso Producto": p.proceso_producto.nombre if p.proceso_producto else "N/A",
            }
            for p in productos
        ]

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = {1: "Productos", 2: "Servicios"}.get(tipo_producto, "Producto")
            column_name = {1: "Producto", 2: "Servicio"}.get(tipo_producto, "Producto")
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            workbook = writer.book
            sheet = workbook[sheet_name]
            sheet.cell(row=1, column=2, value=column_name)
            for col in sheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value and len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except Exception:
                        pass
                sheet.column_dimensions[column].width = max_length + 2

        output.seek(0)
        return output

    def crear_producto(self, producto_data: ProductoCreate):
        nuevo_producto = Producto(**producto_data.model_dump())
        self.db.add(nuevo_producto)
        self.db.commit()
        self.db.refresh(nuevo_producto)

        return self.db.execute(
            select(Producto)
            .options(
                selectinload(Producto.tipo_producto),
                selectinload(Producto.proceso_producto),
                selectinload(Producto.unidad_medida)
            )
            .where(Producto.id == nuevo_producto.id)
        ).scalar_one_or_none()

    def actualizar_producto(self, id: int, producto_data: ProductoUpdate):
        producto_db = self.db.execute(
            select(Producto).where(Producto.id == id)
        ).scalar_one_or_none()

        if not producto_db:
            return None

        for key, value in producto_data.model_dump(exclude_unset=True).items():
            if key in ["unidad_medida_id", "tipo_producto_id", "proceso_producto_id"]:
                if value in [None, 0]:
                    continue
            setattr(producto_db, key, value)

        self.db.commit()
        self.db.refresh(producto_db)
        return producto_db

    