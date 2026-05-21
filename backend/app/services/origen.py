from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.origen import Origen
from app.schemas.origen import OrigenCreate, OrigenUpdate
from typing import Optional
import pandas as pd
import io


class OrigenService:
    def __init__(self, db: Session):
        self.db = db

    def listar_origenes(self):
        return self.db.execute(select(Origen).order_by(Origen.id)).scalars().all()

    def exportar_origenes(self, consulta: Optional[str] = None):
        query = select(Origen).order_by(Origen.id)

        if consulta:
            query = query.where(
                Origen.codigo.ilike(f"%{consulta}%") |
                Origen.nombre.ilike(f"%{consulta}%")
            )

        origenes = self.db.execute(query).scalars().all()

        data = [
            {
                "Codigo": o.codigo,
                "Origen": o.nombre,
            }
            for o in origenes
        ]

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Origenes")
            workbook = writer.book
            sheet = workbook["Origenes"]
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

    def crear_origen(self, origen_data: OrigenCreate):
        nuevo_origen = Origen(**origen_data.model_dump())
        self.db.add(nuevo_origen)
        self.db.commit()
        self.db.refresh(nuevo_origen)
        return nuevo_origen

    def actualizar_origen(self, id: int, origen_data: OrigenUpdate):
        origen_db = self.db.execute(
            select(Origen).where(Origen.id == id)
        ).scalar_one_or_none()

        if not origen_db:
            return None

        for key, value in origen_data.model_dump(exclude_unset=True).items():
            setattr(origen_db, key, value)

        self.db.commit()
        self.db.refresh(origen_db)
        return origen_db

    def eliminar_origen(self, id: int) -> bool:
        origen_db = self.db.execute(
            select(Origen).where(Origen.id == id)
        ).scalar_one_or_none()

        if not origen_db:
            return False

        self.db.delete(origen_db)
        self.db.commit()
        return True