# services/destino.py

from sqlmodel import Session, select
from app.models.registro.modelo_destino import Destino, DestinoCreate, DestinoUpdate
from typing import Optional
import pandas as pd
import io

class DestinoService:
    def __init__(self, db: Session):
        self.db = db

    def listar_destinos(self):
        statement = select(Destino).order_by(Destino.dest_id)
        return self.db.exec(statement).all()
    
    def exportar_destinos(self, consulta: Optional[str] = None):
        # Consultar todos los vehículos
        destinos = select(Destino).order_by(Destino.dest_id)
        
        if consulta:
            destinos = destinos.where(
                (
                    Destino.dest_codigo.ilike(f"%{consulta}%"), 
                    Destino.dest_nombre.ilike(f"%{consulta}%"),
                )
            )
        result = self.db.execute(destinos)
        destinos = result.scalars().all()

        # Preparar los datos para el DataFrame
        data = [
            {
                "Codigo": destino.dest_codigo,
                "Patio": destino.dest_nombre,
            }
            for destino in destinos
        ]

        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = "Destinos"
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

    def crear_destino(self, destino_data: DestinoCreate):
        nuevo_destino = Destino(**destino_data.dict())
        self.db.add(nuevo_destino)
        self.db.commit()
        self.db.refresh(nuevo_destino)

        return nuevo_destino

    def actualizar_destino(self, dest_id: int, destino_data: DestinoUpdate):
        statement = select(Destino).where(Destino.dest_id == dest_id)
        destino_db = self.db.exec(statement).first()
        
        if not destino_db:
            return None  # Si el destino no existe, devolvemos None

        update_data = destino_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(destino_db, key, value)

        self.db.commit()
        self.db.refresh(destino_db)

        return destino_db

    def eliminar_destino(self, dest_id: int) -> bool:
        statement = select(Destino).where(Destino.dest_id == dest_id)
        destino_db = self.db.exec(statement).first()
        
        if not destino_db:
            return False
        
        self.db.delete(destino_db)
        self.db.commit()
        return True
