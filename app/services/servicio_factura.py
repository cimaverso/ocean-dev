# services/factura.py

from sqlmodel import Session, select
from app.models.registro.modelo_factura import Factura, FacturaCreate, FacturaUpdate
from typing import Optional
import pandas as pd
import io

class FacturaService:
    def __init__(self, db: Session):
        self.db = db

    def listar_facturas(self):
        statement = select(Factura).order_by(Factura.fac_id)
        return self.db.exec(statement).all()
    
    def exportar_facturas(self, consulta: Optional[str] = None):
        # Consultar todos los vehículos
        facturas = select(Factura).order_by(Factura.fac_id)
        
        if consulta:
            facturas = facturas.where(
                (
                    Factura.fac_fecha.ilike(f"%{consulta}%"),
                )
            )
        result = self.db.execute(facturas)
        facturas = result.scalars().all()

        # Preparar los datos para el DataFrame
        data = [
            {
                "Factura": factura.fac_fecha,
            }
            for factura in facturas
        ]

        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = "Facturas"
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

    def listar_factura_fecha(self, fac_fecha: str):
        statement = select(Factura).where(Factura.fac_fecha == fac_fecha)
        return self.db.exec(statement).first()

    def crear_factura(self, factura_data: FacturaCreate):
        nueva_factura = Factura(**factura_data.dict())

        self.db.add(nueva_factura)
        self.db.commit()
        self.db.refresh(nueva_factura)

        return nueva_factura

    def actualizar_factura(self, fac_id: int, factura_data: FacturaUpdate):
        statement = select(Factura).where(Factura.fac_id == fac_id)
        factura_db = self.db.exec(statement).first()
        
        if not factura_db:
            return None

        update_data = factura_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(factura_db, key, value)

        self.db.commit()
        self.db.refresh(factura_db)

        return factura_db
    
    def eliminar_factura(self, fac_id: int) -> bool:
        statement = select(Factura).where(Factura.fac_id == fac_id)
        factura_db = self.db.exec(statement).first()
        
        if not factura_db:
            return False
        
        self.db.delete(factura_db)
        self.db.commit()

        return True
