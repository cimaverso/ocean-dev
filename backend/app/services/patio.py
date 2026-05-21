from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.patio import Patio
from app.schemas.patio import PatioCreate, PatioUpdate
from typing import Optional
import pandas as pd
import io


class PatioService:
    def __init__(self, db: Session):
        self.db = db

    def listar_patios(self):
        return self.db.execute(select(Patio).order_by(Patio.id)).scalars().all()

    def exportar_patios(self, consulta: Optional[str] = None):
        query = select(Patio).order_by(Patio.id)

        if consulta:
            query = query.where(
                Patio.codigo.ilike(f"%{consulta}%") |
                Patio.nombre.ilike(f"%{consulta}%")
            )

        patios = self.db.execute(query).scalars().all()

        data = [
            {
                "Codigo": p.codigo,
                "Patio": p.nombre,
            }
            for p in patios
        ]

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Patios")
            workbook = writer.book
            sheet = workbook["Patios"]
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

    def crear_patio(self, patio_data: PatioCreate):
        nuevo_patio = Patio(**patio_data.model_dump())
        self.db.add(nuevo_patio)
        self.db.commit()
        self.db.refresh(nuevo_patio)
        return nuevo_patio

    def actualizar_patio(self, id: int, patio_data: PatioUpdate):
        patio_db = self.db.execute(
            select(Patio).where(Patio.id == id)
        ).scalar_one_or_none()

        if not patio_db:
            return None

        for key, value in patio_data.model_dump(exclude_unset=True).items():
            setattr(patio_db, key, value)

        self.db.commit()
        self.db.refresh(patio_db)
        return patio_db

    def eliminar_patio(self, id: int) -> bool:
        patio_db = self.db.execute(
            select(Patio).where(Patio.id == id)
        ).scalar_one_or_none()

        if not patio_db:
            return False

        self.db.delete(patio_db)
        self.db.commit()
        return True