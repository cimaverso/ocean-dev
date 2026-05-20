from sqlmodel import Session, select
from app.models.registro.modelo_transportadora import Transportadora, TransportadoraCreate, TransportadoraUpdate
from typing import Optional
import pandas as pd
import io

class TransportadoraService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_transportadoras(self):
        statement = select(Transportadora).order_by(Transportadora.trans_id)
        return self.db.exec(statement).all()

    def exportar_transportadoras(self, consulta: Optional[str] = None):
        # Consultar todos los vehículos
        transportadoras = select(Transportadora).order_by(Transportadora.trans_id)
        
        if consulta:
            transportadoras = transportadoras.where(
                (
                    Transportadora.trans_codigo.ilike(f"%{consulta}%"), 
                    Transportadora.trans_nombre.ilike(f"%{consulta}%"),
                    Transportadora.trans_ciudad.ilike(f"%{consulta}%"),
                    Transportadora.trans_nit.ilike(f"%{consulta}%"),
                    Transportadora.trans_telefono.ilike(f"%{consulta}%"),
                    Transportadora.trans_direccion.ilike(f"%{consulta}%")
                )
            )
        result = self.db.execute(transportadoras)
        transportadoras = result.scalars().all()

        # Preparar los datos para el DataFrame
        data = [
            {
                "Codigo": transportadora.trans_codigo,
                "Transportadora": transportadora.trans_nombre,
                "Ciudad": transportadora.trans_ciudad,
                "Nit": transportadora.trans_nit,
                "Telefono": transportadora.trans_telefono,
                "Direccion": transportadora.trans_direccion,
            }
            for transportadora in transportadoras
        ]

        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = "Transportadoras"
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

    def crear_transportadora(self, transportadora_data: TransportadoraCreate):
        nueva_transportadora = Transportadora(
            trans_nombre=transportadora_data.trans_nombre,
            trans_ciudad=transportadora_data.trans_ciudad,
            trans_direccion=transportadora_data.trans_direccion,
            trans_nit=transportadora_data.trans_nit,
            trans_telefono=transportadora_data.trans_telefono,
            trans_codigo=transportadora_data.trans_codigo
        )
        self.db.add(nueva_transportadora)
        self.db.commit()
        self.db.refresh(nueva_transportadora)
        return nueva_transportadora

    def actualizar_transportadora(self, trans_id: int, transportadora_data: TransportadoraUpdate):
        statement = select(Transportadora).where(Transportadora.trans_id == trans_id)
        result = self.db.exec(statement)
        transportadora_db = result.first()

        if not transportadora_db:
            return None  # No se encontró la transportadora

        update_data = transportadora_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(transportadora_db, key, value)

        self.db.add(transportadora_db)
        self.db.commit()
        self.db.refresh(transportadora_db)
        return transportadora_db

    def eliminar_transportadora(self, trans_id: int) -> bool:
        statement = select(Transportadora).where(Transportadora.trans_id == trans_id)
        result = self.db.exec(statement)
        transportadora_db = result.first()

        if not transportadora_db:
            return False  # No se encontró la transportadora

        self.db.delete(transportadora_db)
        self.db.commit()
        return True

