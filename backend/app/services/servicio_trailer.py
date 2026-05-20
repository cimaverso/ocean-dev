from sqlmodel import Session, select
from app.models.registro.modelo_trailer import Trailer,TrailerCreate, TrailerUpdate
from typing import Optional
import pandas as pd
import io

class TrailerService:
    def __init__(self, db: Session):
        self.db = db

    def listar_trailers(self):
        return self.db.query(Trailer).order_by(Trailer.trai_id).all()
    
    def exportar_trailers(self, consulta: Optional[str] = None):
        # Consultar todos los vehículos
        trailers = select(Trailer).order_by(Trailer.trai_id)
        
        if consulta:
            trailers = trailers.where(
                (
                    Trailer.trai_placa.ilike(f"%{consulta}%")    
                )
            )
        result = self.db.execute(trailers)
        trailers = result.scalars().all()

        # Preparar los datos para el DataFrame
        data = [
            {
                "Trailer": trailer.trai_placa,
            }
            for trailer in trailers
        ]

        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = "Trailers"
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

    def crear_trailer(self, trailer_data: TrailerCreate):
        nuevo_trailer = Trailer(**trailer_data.dict())
        self.db.add(nuevo_trailer)
        self.db.commit()
        self.db.refresh(nuevo_trailer)
        return nuevo_trailer

    def actualizar_trailer(self, trai_id: int, trailer_data: TrailerUpdate):
        trailer_db = self.db.query(Trailer).filter(Trailer.trai_id == trai_id).first()

        if not trailer_db:
            return None  # Si no se encuentra el trailer, devolvemos None

        # Actualizar solo los campos proporcionados
        update_data = trailer_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(trailer_db, key, value)

        self.db.commit()
        self.db.refresh(trailer_db)
        return trailer_db
    
    def eliminar_trailer(self, trai_id: int) -> bool:
        trailer_db = self.db.query(Trailer).filter(Trailer.trai_id == trai_id).first()
        
        if not trailer_db:
            return False  
        
        self.db.delete(trailer_db)
        self.db.commit()

        return True  # Eliminación exitosa

