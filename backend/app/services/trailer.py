from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.trailer import Trailer
from app.schemas.trailer import TrailerCreate, TrailerUpdate
from typing import Optional
import pandas as pd
import io


class TrailerService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_trailers(self):
        return self.db.execute(select(Trailer).order_by(Trailer.id)).scalars().all()

    def exportar_trailers(self, consulta: Optional[str] = None):
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

    def crear_trailer(self, trailer_data: TrailerCreate):
        nuevo_trailer = Trailer(**trailer_data.model_dump())
        self.db.add(nuevo_trailer)
        self.db.commit()
        self.db.refresh(nuevo_trailer)
        return nuevo_trailer

    def actualizar_trailer(self, id: int, trailer_data: TrailerUpdate):
        trailer_db = self.db.execute(
            select(Trailer).where(Trailer.id == id)
        ).scalar_one_or_none()

        if not trailer_db:
            return None

        for key, value in trailer_data.model_dump(exclude_unset=True).items():
            setattr(trailer_db, key, value)

        self.db.commit()
        self.db.refresh(trailer_db)
        return trailer_db

    