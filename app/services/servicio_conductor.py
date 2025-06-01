from sqlmodel import Session, select
from app.models.registro.modelo_conductor import Conductor, ConductorCreate, ConductorUpdate
from typing import Optional
import pandas as pd
import io

class ConductorService:
    def __init__(self, db: Session):
        self.db = db

    def listar_conductores(self):
        statement = select(Conductor).order_by(Conductor.conduct_id)
        return self.db.exec(statement).all()
    
    def exportar_conductores(self, consulta: Optional[str] = None):
        # Consultar todos los vehículos
        conductores = select(Conductor).order_by(Conductor.conduct_id)
        
        if consulta:
            conductores = conductores.where(
                (
                    Conductor.conduct_codigo.ilike(f"%{consulta}%"),
                    Conductor.conduct_nombre.ilike(f"%{consulta}%"),
                    Conductor.conduct_cedula.ilike(f"%{consulta}%"),
                    Conductor.conduct_telefono.ilike(f"%{consulta}%")

                )
            )
        result = self.db.execute(conductores)
        conductores = result.scalars().all()

        # Preparar los datos para el DataFrame
        data = [
            {
                "Código": conductor.conduct_codigo,
                "Conductor": conductor.conduct_nombre,
                "Cedula": conductor.conduct_cedula,
                "Teléfono": conductor.conduct_telefono
            }
            for conductor in conductores
        ]

        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = "Conductores"
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
    

    def crear_conductor(self, conductor_data: ConductorCreate):
        nuevo_conductor = Conductor(**conductor_data.dict())
        self.db.add(nuevo_conductor)
        self.db.commit()
        self.db.refresh(nuevo_conductor)
        return nuevo_conductor

    def actualizar_conductor(self, conduct_id: int, conductor_data: ConductorUpdate):
        statement = select(Conductor).where(Conductor.conduct_id == conduct_id)
        conductor_db = self.db.exec(statement).first()

        if not conductor_db:
            return None

        update_data = conductor_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(conductor_db, key, value)

        self.db.commit()
        self.db.refresh(conductor_db)
        return conductor_db
    
    def eliminar_conductor(self, conduct_id: int) -> bool:
        statement = select(Conductor).where(Conductor.conduct_id == conduct_id)
        conductor_db = self.db.exec(statement).first()

        if not conductor_db:
            return False

        self.db.delete(conductor_db)
        self.db.commit()
        return True
