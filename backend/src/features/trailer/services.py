from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
import pandas as pd
import io

from src.features.trailer.models import Trailer
from src.features.trailer.schemas import TrailerCreate, TrailerUpdate


class TrailerService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_trailers(self) -> list[Trailer]:
        return self.db.execute(
            select(Trailer).order_by(Trailer.id)
        ).scalars().all()

    def exportar_trailers(self, consulta: Optional[str] = None) -> io.BytesIO:
        query = select(Trailer).order_by(Trailer.id)
        if consulta:
            query = query.where(Trailer.placa.ilike(f"%{consulta}%"))
        trailers = self.db.execute(query).scalars().all()
        data = [{"Trailer": t.placa} for t in trailers]
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Trailers")
            workbook = writer.book
            sheet = workbook["Trailers"]
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

    def crear_trailer(self, data: TrailerCreate) -> Trailer:
        nuevo = Trailer(**data.model_dump())
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def actualizar_trailer(self, id: int, data: TrailerUpdate) -> Trailer | None:
        trailer = self.db.execute(
            select(Trailer).where(Trailer.id == id)
        ).scalar_one_or_none()
        if not trailer:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(trailer, key, value)
        self.db.commit()
        self.db.refresh(trailer)
        return trailer