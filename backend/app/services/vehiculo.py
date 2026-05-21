from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.vehiculo import Vehiculo
from app.schemas.vehiculo import VehiculoCreate, VehiculoUpdate
from typing import Optional
import pandas as pd
import io


class VehiculoService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_vehiculos(self):
        return self.db.execute(select(Vehiculo).order_by(Vehiculo.id)).scalars().all()

    def exportar_vehiculos(self, consulta: Optional[str] = None):
        query = select(Vehiculo).order_by(Vehiculo.id)

        if consulta:
            query = query.where(Vehiculo.placa.ilike(f"%{consulta}%"))

        vehiculos = self.db.execute(query).scalars().all()

        data = [{"Placa": v.placa} for v in vehiculos]

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Vehículos")
            workbook = writer.book
            sheet = workbook["Vehículos"]
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

    def crear_vehiculo(self, vehiculo_data: VehiculoCreate):
        nuevo_vehiculo = Vehiculo(**vehiculo_data.model_dump())
        self.db.add(nuevo_vehiculo)
        self.db.commit()
        self.db.refresh(nuevo_vehiculo)
        return nuevo_vehiculo

    def actualizar_vehiculo(self, id: int, vehiculo_data: VehiculoUpdate):
        vehiculo_db = self.db.execute(
            select(Vehiculo).where(Vehiculo.id == id)
        ).scalar_one_or_none()

        if not vehiculo_db:
            return None

        for key, value in vehiculo_data.model_dump(exclude_unset=True).items():
            setattr(vehiculo_db, key, value)

        self.db.commit()
        self.db.refresh(vehiculo_db)
        return vehiculo_db

    def eliminar_vehiculo(self, id: int) -> bool:
        vehiculo_db = self.db.execute(
            select(Vehiculo).where(Vehiculo.id == id)
        ).scalar_one_or_none()

        if not vehiculo_db:
            return False

        self.db.delete(vehiculo_db)
        self.db.commit()
        return True