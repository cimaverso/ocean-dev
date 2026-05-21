from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.factura import Factura
from app.schemas.factura import FacturaCreate, FacturaUpdate
from typing import Optional
import pandas as pd
import io


class FacturaService:
    def __init__(self, db: Session):
        self.db = db

    def listar_facturas(self):
        return self.db.execute(select(Factura).order_by(Factura.id)).scalars().all()

    def exportar_facturas(self, consulta: Optional[str] = None):
        query = select(Factura).order_by(Factura.id)

        if consulta:
            query = query.where(Factura.fecha.ilike(f"%{consulta}%"))

        facturas = self.db.execute(query).scalars().all()

        data = [{"Factura": f.fecha} for f in facturas]

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Facturas")
            workbook = writer.book
            sheet = workbook["Facturas"]
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

    def listar_factura_fecha(self, fecha: str):
        return self.db.execute(
            select(Factura).where(Factura.fecha == fecha)
        ).scalar_one_or_none()

    def crear_factura(self, factura_data: FacturaCreate):
        nueva_factura = Factura(**factura_data.model_dump())
        self.db.add(nueva_factura)
        self.db.commit()
        self.db.refresh(nueva_factura)
        return nueva_factura

    def actualizar_factura(self, id: int, factura_data: FacturaUpdate):
        factura_db = self.db.execute(
            select(Factura).where(Factura.id == id)
        ).scalar_one_or_none()

        if not factura_db:
            return None

        for key, value in factura_data.model_dump(exclude_unset=True).items():
            setattr(factura_db, key, value)

        self.db.commit()
        self.db.refresh(factura_db)
        return factura_db

    