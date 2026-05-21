from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.destino import Destino
from app.schemas.destino import DestinoCreate, DestinoUpdate
from typing import Optional
import pandas as pd
import io


class DestinoService:
    def __init__(self, db: Session):
        self.db = db

    def listar_destinos(self):
        return self.db.execute(select(Destino).order_by(Destino.id)).scalars().all()

    def exportar_destinos(self, consulta: Optional[str] = None):
        query = select(Destino).order_by(Destino.id)

        if consulta:
            query = query.where(
                Destino.codigo.ilike(f"%{consulta}%") |
                Destino.nombre.ilike(f"%{consulta}%")
            )

        destinos = self.db.execute(query).scalars().all()

        data = [
            {
                "Codigo": d.codigo,
                "Destino": d.nombre,
            }
            for d in destinos
        ]

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Destinos")
            workbook = writer.book
            sheet = workbook["Destinos"]
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

    def crear_destino(self, destino_data: DestinoCreate):
        nuevo_destino = Destino(**destino_data.model_dump())
        self.db.add(nuevo_destino)
        self.db.commit()
        self.db.refresh(nuevo_destino)
        return nuevo_destino

    def actualizar_destino(self, id: int, destino_data: DestinoUpdate):
        destino_db = self.db.execute(
            select(Destino).where(Destino.id == id)
        ).scalar_one_or_none()

        if not destino_db:
            return None

        for key, value in destino_data.model_dump(exclude_unset=True).items():
            setattr(destino_db, key, value)

        self.db.commit()
        self.db.refresh(destino_db)
        return destino_db

    