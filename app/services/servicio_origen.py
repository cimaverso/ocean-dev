# services/origen.py

from sqlmodel import Session, select
from app.models.registro.modelo_origen import Origen,OrigenCreate, OrigenUpdate
from typing import Optional
import pandas as pd
import io

class OrigenService:
    def __init__(self, db: Session):
        self.db = db

    def listar_origenes(self):

        statement = select(Origen).order_by(Origen.ori_id)
        return self.db.exec(statement).all()
       
    def exportar_origenes(self, consulta: Optional[str] = None):
        # Consultar todos los vehículos
        origenes = select(Origen).order_by(Origen.ori_id)
        
        if consulta:
            origenes = origenes.where(
                (
                    Origen.ori_codigo.ilike(f"%{consulta}%"), 
                    Origen.ori_nombre.ilike(f"%{consulta}%"),
                )
            )
        result = self.db.execute(origenes)
        origenes = result.scalars().all()

        # Preparar los datos para el DataFrame
        data = [
            {
                "Codigo": origen.ori_codigo,
                "Patio": origen.ori_nombre,
            }
            for origen in origenes
        ]

        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = "Origenes"
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

    def crear_origen(self, origen_data: OrigenCreate):
        nuevo_origen = Origen(**origen_data.dict())

        self.db.add(nuevo_origen)
        self.db.commit()
        self.db.refresh(nuevo_origen)

        return nuevo_origen

    def actualizar_origen(self, ori_id: int, origen_data: OrigenUpdate):
        statement = select(Origen).where(Origen.ori_id == ori_id)
        origen_db = self.db.exec(statement).first()
        
        if not origen_db:
            return None

        update_data = origen_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(origen_db, key, value)

        self.db.commit()
        self.db.refresh(origen_db)

        return origen_db
    
    def eliminar_origen(self, ori_id: int) -> bool:
        statement = select(Origen).where(Origen.ori_id == ori_id)
        origen_db = self.db.exec(statement).first()
        
        if not origen_db:
            return False
        
        self.db.delete(origen_db)
        self.db.commit()

        return True
