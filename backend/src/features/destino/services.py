from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
import pandas as pd
import io

from src.features.destino.models import Destino
from src.features.destino.schemas import DestinoCreate, DestinoUpdate


class DestinoService:
    def __init__(self, db: Session):
        self.db = db

    def listar_destinos(self) -> list[Destino]:
        return self.db.execute(select(Destino).order_by(Destino.id)).scalars().all()

    def exportar_destinos(self, consulta: Optional[str] = None) -> io.BytesIO:
        query = select(Destino).order_by(Destino.id)
        if consulta:
            query = query.where(
                Destino.codigo.ilike(f"%{consulta}%") |
                Destino.nombre.ilike(f"%{consulta}%")
            )
        destinos = self.db.execute(query).scalars().all()
        data = [{"Codigo": d.codigo, "Destino": d.nombre} for d in destinos]
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Destinos")
            sheet = writer.book["Destinos"]
            for col in sheet.columns:
                max_length = max((len(str(cell.value)) for cell in col if cell.value), default=0)
                sheet.column_dimensions[col[0].column_letter].width = max_length + 2
        output.seek(0)
        return output

    def crear_destino(self, data: DestinoCreate) -> Destino:
        nuevo = Destino(**data.model_dump())
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def actualizar_destino(self, id: int, data: DestinoUpdate) -> Destino | None:
        destino = self.db.execute(select(Destino).where(Destino.id == id)).scalar_one_or_none()
        if not destino:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(destino, key, value)
        self.db.commit()
        self.db.refresh(destino)
        return destino