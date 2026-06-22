from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from typing import Optional
import pandas as pd
import io

from src.features.producto.models import Producto, ProcesoProducto
from src.features.medida.models import UnidadMedida
from src.features.producto.schemas import ProductoCreate, ProductoUpdate


def _load_all(query):
    return query.options(
        selectinload(Producto.tipo_producto),
        selectinload(Producto.proceso_producto),
        selectinload(Producto.unidad_medida),
    )


class ProductoService:
    def __init__(self, db: Session):
        self.db = db

    def listar_productos_tipo(self, tipo: int) -> list[Producto]:
        return self.db.execute(
            _load_all(select(Producto).where(Producto.tipo_producto_id == tipo).order_by(Producto.id))
        ).scalars().all()

    def listar_procesos(self) -> list[ProcesoProducto]:
        return self.db.execute(select(ProcesoProducto).order_by(ProcesoProducto.id)).scalars().all()

    def exportar_productos(self, tipo_producto: int, consulta: Optional[str] = None) -> io.BytesIO:
        query = select(Producto).where(Producto.tipo_producto_id == tipo_producto)
        if consulta:
            query = query.where(
                Producto.codigo.ilike(f"%{consulta}%") |
                Producto.nombre.ilike(f"%{consulta}%") |
                Producto.unidad_medida.has(UnidadMedida.nombre.ilike(f"%{consulta}%")) |
                Producto.proceso_producto.has(ProcesoProducto.nombre.ilike(f"%{consulta}%"))
            )
        productos = self.db.execute(query).scalars().all()
        data = [{
            "Codigo": p.codigo,
            "Producto": p.nombre,
            "Unidad Medida": p.unidad_medida.nombre if p.unidad_medida else "N/A",
            "Proceso Producto": p.proceso_producto.nombre if p.proceso_producto else "N/A",
        } for p in productos]
        sheet_name = {1: "Productos", 2: "Servicios"}.get(tipo_producto, "Producto")
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            sheet = writer.book[sheet_name]
            for col in sheet.columns:
                max_length = max((len(str(cell.value)) for cell in col if cell.value), default=0)
                sheet.column_dimensions[col[0].column_letter].width = max_length + 2
        output.seek(0)
        return output

    def crear_producto(self, data: ProductoCreate) -> Producto:
        nuevo = Producto(**data.model_dump())
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return self.db.execute(
            _load_all(select(Producto).where(Producto.id == nuevo.id))
        ).scalar_one_or_none()

    def actualizar_producto(self, id: int, data: ProductoUpdate) -> Producto | None:
        producto = self.db.execute(select(Producto).where(Producto.id == id)).scalar_one_or_none()
        if not producto:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            if key in ["unidad_medida_id", "tipo_producto_id", "proceso_producto_id"] and not value:
                continue
            setattr(producto, key, value)
        self.db.commit()
        self.db.refresh(producto)
        return producto