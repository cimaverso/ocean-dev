from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
import pandas as pd
import io

from src.features.comprador.models import Comprador
from src.features.comprador.schemas import CompradorCreate, CompradorUpdate


class CompradorService:
    def __init__(self, db: Session):
        self.db = db

    def listar_compradores(self) -> list[Comprador]:
        return self.db.execute(
            select(Comprador).order_by(Comprador.id)
        ).scalars().all()

    def exportar_compradores(self, consulta: Optional[str] = None) -> io.BytesIO:
        query = select(Comprador).order_by(Comprador.id)
        if consulta:
            query = query.where(
                Comprador.codigo.ilike(f"%{consulta}%") |
                Comprador.nombre.ilike(f"%{consulta}%") |
                Comprador.nit.ilike(f"%{consulta}%") |
                Comprador.telefono.ilike(f"%{consulta}%")
            )
        compradores = self.db.execute(query).scalars().all()
        data = [
            {
                "Codigo": c.codigo,
                "Comprador": c.nombre,
                "Nit": c.nit,
                "Telefono": c.telefono,
            }
            for c in compradores
        ]
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Compradores")
            workbook = writer.book
            sheet = workbook["Compradores"]
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

    def crear_comprador(self, data: CompradorCreate) -> Comprador:
        nuevo = Comprador(**data.model_dump())
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def actualizar_comprador(self, id: int, data: CompradorUpdate) -> Comprador | None:
        comprador = self.db.execute(
            select(Comprador).where(Comprador.id == id)
        ).scalar_one_or_none()
        if not comprador:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(comprador, key, value)
        self.db.commit()
        self.db.refresh(comprador)
        return comprador