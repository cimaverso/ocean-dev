from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.conductor import Conductor
from app.schemas.conductor import ConductorCreate, ConductorUpdate
from typing import Optional
import pandas as pd
import io


class ConductorService:
    def __init__(self, db: Session):
        self.db = db

    def listar_conductores(self):
        return self.db.execute(select(Conductor).order_by(Conductor.id)).scalars().all()

    def exportar_conductores(self, consulta: Optional[str] = None):
        query = select(Conductor).order_by(Conductor.id)

        if consulta:
            query = query.where(
                Conductor.nombre.ilike(f"%{consulta}%") |
                Conductor.cedula.ilike(f"%{consulta}%") |
                Conductor.telefono.ilike(f"%{consulta}%")
            )

        conductores = self.db.execute(query).scalars().all()

        data = [
            {
                "Conductor": c.nombre,
                "Cedula": c.cedula,
                "Teléfono": c.telefono,
            }
            for c in conductores
        ]

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Conductores")
            workbook = writer.book
            sheet = workbook["Conductores"]
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

    def crear_conductor(self, conductor_data: ConductorCreate):
        nuevo_conductor = Conductor(**conductor_data.model_dump())
        self.db.add(nuevo_conductor)
        self.db.commit()
        self.db.refresh(nuevo_conductor)
        return nuevo_conductor

    def actualizar_conductor(self, id: int, conductor_data: ConductorUpdate):
        conductor_db = self.db.execute(
            select(Conductor).where(Conductor.id == id)
        ).scalar_one_or_none()

        if not conductor_db:
            return None

        for key, value in conductor_data.model_dump(exclude_unset=True).items():
            setattr(conductor_db, key, value)

        self.db.commit()
        self.db.refresh(conductor_db)
        return conductor_db

    def eliminar_conductor(self, id: int) -> bool:
        conductor_db = self.db.execute(
            select(Conductor).where(Conductor.id == id)
        ).scalar_one_or_none()

        if not conductor_db:
            return False

        self.db.delete(conductor_db)
        self.db.commit()
        return True