from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
import pandas as pd
import io

from src.features.factura.models import Factura
from src.features.factura.schemas import FacturaCreate, FacturaUpdate


class FacturaService:
    def __init__(self, db: Session):
        self.db = db

    def listar_facturas(self) -> list[Factura]:
        return self.db.execute(select(Factura).order_by(Factura.id)).scalars().all()

    def listar_factura_fecha(self, fecha: str) -> Factura | None:
        return self.db.execute(select(Factura).where(Factura.fecha == fecha)).scalar_one_or_none()

    def exportar_facturas(self, consulta: Optional[str] = None) -> io.BytesIO:
        query = select(Factura).order_by(Factura.id)
        if consulta:
            query = query.where(Factura.fecha.ilike(f"%{consulta}%"))
        facturas = self.db.execute(query).scalars().all()
        data = [{"Factura": f.fecha} for f in facturas]
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Facturas")
            sheet = writer.book["Facturas"]
            for col in sheet.columns:
                max_length = max((len(str(cell.value)) for cell in col if cell.value), default=0)
                sheet.column_dimensions[col[0].column_letter].width = max_length + 2
        output.seek(0)
        return output

    def crear_factura(self, data: FacturaCreate) -> Factura:
        nueva = Factura(**data.model_dump())
        self.db.add(nueva)
        self.db.commit()
        self.db.refresh(nueva)
        return nueva

    def actualizar_factura(self, id: int, data: FacturaUpdate) -> Factura | None:
        factura = self.db.execute(select(Factura).where(Factura.id == id)).scalar_one_or_none()
        if not factura:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(factura, key, value)
        self.db.commit()
        self.db.refresh(factura)
        return factura