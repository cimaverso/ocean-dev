from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
import pandas as pd
import io

from src.features.patio.models import Patio
from src.features.patio.schemas import PatioCreate, PatioUpdate


class PatioService:
    def __init__(self, db: Session):
        self.db = db

    def listar_patios(self) -> list[Patio]:
        return self.db.execute(select(Patio).order_by(Patio.id)).scalars().all()

    def exportar_patios(self, consulta: Optional[str] = None) -> io.BytesIO:
        query = select(Patio).order_by(Patio.id)
        if consulta:
            query = query.where(
                Patio.codigo.ilike(f"%{consulta}%") |
                Patio.nombre.ilike(f"%{consulta}%")
            )
        patios = self.db.execute(query).scalars().all()
        data = [{"Codigo": p.codigo, "Patio": p.nombre} for p in patios]
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Patios")
            sheet = writer.book["Patios"]
            for col in sheet.columns:
                max_length = max((len(str(cell.value)) for cell in col if cell.value), default=0)
                sheet.column_dimensions[col[0].column_letter].width = max_length + 2
        output.seek(0)
        return output

    def crear_patio(self, data: PatioCreate) -> Patio:
        nuevo = Patio(**data.model_dump())
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def actualizar_patio(self, id: int, data: PatioUpdate) -> Patio | None:
        patio = self.db.execute(select(Patio).where(Patio.id == id)).scalar_one_or_none()
        if not patio:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(patio, key, value)
        self.db.commit()
        self.db.refresh(patio)
        return patio