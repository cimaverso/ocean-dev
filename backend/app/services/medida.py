from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.unidad_medida import UnidadMedida
from app.schemas.unidad_medida import UnidadMedidaCreate, UnidadMedidaUpdate
from typing import Optional
import pandas as pd
import io


class UnidadMedidaService:
    def __init__(self, db: Session):
        self.db = db

    def listar_medidas(self):
        return self.db.execute(select(UnidadMedida).order_by(UnidadMedida.id)).scalars().all()

    def exportar_medidas(self, consulta: Optional[str] = None):
        query = select(UnidadMedida).order_by(UnidadMedida.id)

        if consulta:
            query = query.where(UnidadMedida.nombre.ilike(f"%{consulta}%"))

        medidas = self.db.execute(query).scalars().all()

        data = [{"Unidad Medida": m.nombre} for m in medidas]

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Medidas")
            workbook = writer.book
            sheet = workbook["Medidas"]
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

    def crear_medida(self, medida_data: UnidadMedidaCreate):
        nueva_medida = UnidadMedida(**medida_data.model_dump())
        self.db.add(nueva_medida)
        self.db.commit()
        self.db.refresh(nueva_medida)
        return nueva_medida

    def actualizar_medida(self, id: int, medida_data: UnidadMedidaUpdate):
        medida_db = self.db.execute(
            select(UnidadMedida).where(UnidadMedida.id == id)
        ).scalar_one_or_none()

        if not medida_db:
            return None

        for key, value in medida_data.model_dump(exclude_unset=True).items():
            setattr(medida_db, key, value)

        self.db.commit()
        self.db.refresh(medida_db)
        return medida_db

    def eliminar_medida(self, id: int) -> bool:
        medida_db = self.db.execute(
            select(UnidadMedida).where(UnidadMedida.id == id)
        ).scalar_one_or_none()

        if not medida_db:
            return False

        self.db.delete(medida_db)
        self.db.commit()
        return True