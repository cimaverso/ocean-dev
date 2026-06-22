from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
import pandas as pd
import io

from src.features.medida.models import UnidadMedida
from src.features.medida.schemas import UnidadMedidaCreate, UnidadMedidaUpdate


class UnidadMedidaService:
    def __init__(self, db: Session):
        self.db = db

    def listar_medidas(self) -> list[UnidadMedida]:
        return self.db.execute(select(UnidadMedida).order_by(UnidadMedida.id)).scalars().all()

    def exportar_medidas(self, consulta: Optional[str] = None) -> io.BytesIO:
        query = select(UnidadMedida).order_by(UnidadMedida.id)
        if consulta:
            query = query.where(UnidadMedida.nombre.ilike(f"%{consulta}%"))
        medidas = self.db.execute(query).scalars().all()
        data = [{"Unidad Medida": m.nombre} for m in medidas]
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Medidas")
            sheet = writer.book["Medidas"]
            for col in sheet.columns:
                max_length = max((len(str(cell.value)) for cell in col if cell.value), default=0)
                sheet.column_dimensions[col[0].column_letter].width = max_length + 2
        output.seek(0)
        return output

    def crear_medida(self, data: UnidadMedidaCreate) -> UnidadMedida:
        nueva = UnidadMedida(**data.model_dump())
        self.db.add(nueva)
        self.db.commit()
        self.db.refresh(nueva)
        return nueva

    def actualizar_medida(self, id: int, data: UnidadMedidaUpdate) -> UnidadMedida | None:
        medida = self.db.execute(select(UnidadMedida).where(UnidadMedida.id == id)).scalar_one_or_none()
        if not medida:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(medida, key, value)
        self.db.commit()
        self.db.refresh(medida)
        return medida