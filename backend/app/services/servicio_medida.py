# services/medida.py

from sqlmodel import Session, select
from app.models.registro.producto.modelo_unidadmedida import UnidadMedida,UnidadMedidaCreate, UnidadMedidaUpdate
from typing import Optional
import pandas as pd
import io

class UnidadMedidaService:
    def __init__(self, db: Session):
        self.db = db

    def listar_medidas(self):
        statement = select(UnidadMedida).order_by(UnidadMedida.um_id)
        return self.db.exec(statement).all()

    def exportar_medidas(self, consulta: Optional[str] = None):
        # Consultar todos los vehículos
        medidas = select(UnidadMedida).order_by(UnidadMedida.um_id)
        
        if consulta:
            medidas = medidas.where(
                (
                    UnidadMedida.um_nombre.ilike(f"%{consulta}%"),
                )
            )
        result = self.db.execute(medidas)
        medidas = result.scalars().all()

        # Preparar los datos para el DataFrame
        data = [
            {
                
                "Unidad Medida": medida.um_nombre,
            }
            for medida in medidas
        ]

        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = "Medidas"
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

    def crear_medida(self, medida_data: UnidadMedidaCreate):
        nueva_medida = UnidadMedida(**medida_data.dict())

        self.db.add(nueva_medida)
        self.db.commit()
        self.db.refresh(nueva_medida)

        return nueva_medida

    def actualizar_medida(self, um_id: int, medida_data: UnidadMedidaUpdate):
        statement = select(UnidadMedida).where(UnidadMedida.um_id == um_id)
        medida_db = self.db.exec(statement).first()
        
        if not medida_db:
            return None

        update_data = medida_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(medida_db, key, value)

        self.db.commit()
        self.db.refresh(medida_db)

        return medida_db
    
    def eliminar_medida(self, um_id: int) -> bool:
        statement = select(UnidadMedida).where(UnidadMedida.um_id == um_id)
        medida_db = self.db.exec(statement).first()
        
        if not medida_db:
            return False
        
        self.db.delete(medida_db)
        self.db.commit()

        return True
