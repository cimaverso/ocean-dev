from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
import pandas as pd
import io

from src.features.origen.models import Origen
from src.features.origen.schemas import OrigenCreate, OrigenUpdate


class OrigenService:
    def __init__(self, db: Session):
        self.db = db

    def listar_origenes(self) -> list[Origen]:
        return self.db.execute(select(Origen).order_by(Origen.id)).scalars().all()

    def exportar_origenes(self, consulta: Optional[str] = None) -> io.BytesIO:
        query = select(Origen).order_by(Origen.id)
        if consulta:
            query = query.where(
                Origen.codigo.ilike(f"%{consulta}%") |
                Origen.nombre.ilike(f"%{consulta}%")
            )
        origenes = self.db.execute(query).scalars().all()
        data = [{"Codigo": o.codigo, "Origen": o.nombre} for o in origenes]
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Origenes")
            sheet = writer.book["Origenes"]
            for col in sheet.columns:
                max_length = max((len(str(cell.value)) for cell in col if cell.value), default=0)
                sheet.column_dimensions[col[0].column_letter].width = max_length + 2
        output.seek(0)
        return output

    def crear_origen(self, data: OrigenCreate) -> Origen:
        nuevo = Origen(**data.model_dump())
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def actualizar_origen(self, id: int, data: OrigenUpdate) -> Origen | None:
        origen = self.db.execute(select(Origen).where(Origen.id == id)).scalar_one_or_none()
        if not origen:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(origen, key, value)
        self.db.commit()
        self.db.refresh(origen)
        return origen