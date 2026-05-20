# services/patio.py

from sqlmodel import Session, select
from app.models.registro.modelo_patio import Patio,PatioCreate, PatioUpdate
from typing import Optional
import pandas as pd
import io

class PatioService:
    def __init__(self, db: Session):
        self.db = db

    def listar_patios(self):
        statement = select(Patio).order_by(Patio.pat_id)
        return self.db.exec(statement).all()

    def exportar_patios(self, consulta: Optional[str] = None):
        # Consultar todos los vehículos
        patios = select(Patio).order_by(Patio.pat_id)
        
        if consulta:
            patios = patios.where(
                (
                    Patio.pat_codigo.ilike(f"%{consulta}%"), 
                    Patio.pat_nombre.ilike(f"%{consulta}%"),
                )
            )
        result = self.db.execute(patios)
        patios = result.scalars().all()

        # Preparar los datos para el DataFrame
        data = [
            {
                "Codigo": patio.pat_codigo,
                "Patio": patio.pat_nombre,
            }
            for patio in patios
        ]

        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = "Patios"
            df.to_excel(writer, index=False, sheet_name=sheet_name)

            # Obtener el libro y hoja activa
            workbook = writer.book
            sheet = workbook[sheet_name]

            # Ajustar el ancho de las columnas
            for col in sheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value and len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = max_length + 2
                sheet.column_dimensions[column].width = adjusted_width

        output.seek(0)
        return output

    def crear_patio(self, patio_data: PatioCreate):
        nuevo_patio = Patio(**patio_data.dict())

        self.db.add(nuevo_patio)
        self.db.commit()
        self.db.refresh(nuevo_patio)

        return nuevo_patio

    def actualizar_patio(self, pat_id: int, patio_data: PatioUpdate):
        statement = select(Patio).where(Patio.pat_id == pat_id)
        patio_db = self.db.exec(statement).first()
        
        if not patio_db:
            return None

        update_data = patio_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(patio_db, key, value)

        self.db.commit()
        self.db.refresh(patio_db)

        return patio_db
    
    def eliminar_patio(self, pat_id: int) -> bool:
        statement = select(Patio).where(Patio.ori_id == pat_id)
        patio_db = self.db.exec(statement).first()
        
        if not patio_db:
            return False
        
        self.db.delete(patio_db)
        self.db.commit()

        return True
