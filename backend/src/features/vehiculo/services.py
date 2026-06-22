from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
import pandas as pd
import io

from src.features.vehiculo.models import Vehiculo
from src.features.vehiculo.schemas import VehiculoCreate, VehiculoUpdate


class VehiculoService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_vehiculos(self) -> list[Vehiculo]:
        return self.db.execute(
            select(Vehiculo).order_by(Vehiculo.id)
        ).scalars().all()

    def exportar_vehiculos(self, consulta: Optional[str] = None) -> io.BytesIO:
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

    def crear_vehiculo(self, data: VehiculoCreate) -> Vehiculo:
        nuevo = Vehiculo(**data.model_dump())
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def actualizar_vehiculo(self, id: int, data: VehiculoUpdate) -> Vehiculo | None:
        vehiculo = self.db.execute(
            select(Vehiculo).where(Vehiculo.id == id)
        ).scalar_one_or_none()
        if not vehiculo:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(vehiculo, key, value)
        self.db.commit()
        self.db.refresh(vehiculo)
        return vehiculo

    def eliminar_vehiculo(self, id: int) -> bool:
        vehiculo = self.db.execute(
            select(Vehiculo).where(Vehiculo.id == id)
        ).scalar_one_or_none()
        if not vehiculo:
            return False
        self.db.delete(vehiculo)
        self.db.commit()
        return True