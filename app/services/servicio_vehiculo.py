from sqlmodel import Session, select
from app.models.registro.modelo_vehiculo import Vehiculo, VehiculoCreate, VehiculoUpdate
import pandas as pd
import io
from typing import Optional

class VehiculoService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_vehiculos(self):
        # Usamos select() en lugar de query()
        statement = select(Vehiculo).order_by(Vehiculo.vehi_id)
        return self.db.exec(statement).all()  # Ejecutamos la consulta y obtenemos todos los resultados
    
    def exportar_vehiculos(self, consulta: Optional[str] = None):
        # Consultar todos los vehículos
        vehiculos = select(Vehiculo).order_by(Vehiculo.vehi_id)
        
        if consulta:
            vehiculos = vehiculos.where(
                (
                    Vehiculo.vehi_placa.ilike(f"%{consulta}%")    
                )
            )
        result = self.db.execute(vehiculos)
        vehiculos = result.scalars().all()

        # Preparar los datos para el DataFrame
        data = [
            {
                "Placa": vehiculo.vehi_placa,
            }
            for vehiculo in vehiculos
        ]

        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = "Vehículos"
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
    
    def crear_vehiculo(self, vehiculo_data: VehiculoCreate):
        # Creamos una nueva instancia de Vehiculo
        nuevo_vehiculo = Vehiculo(vehi_placa=vehiculo_data.vehi_placa)
        self.db.add(nuevo_vehiculo)  # Añadimos el objeto a la sesión
        self.db.commit()  # Confirmamos los cambios
        self.db.refresh(nuevo_vehiculo)  # Refrescamos la instancia con los datos de la DB
        return nuevo_vehiculo

    def actualizar_vehiculo(self, vehi_id: int, vehiculo_data: VehiculoUpdate):
        # Usamos select() para encontrar el vehículo
        statement = select(Vehiculo).where(Vehiculo.vehi_id == vehi_id)
        vehiculo_db = self.db.exec(statement).first()

        if not vehiculo_db:
            return None  # Si no se encuentra el vehículo, devolvemos None

        # Actualizamos solo los campos proporcionados
        update_data = vehiculo_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(vehiculo_db, key, value)

        self.db.commit()
        self.db.refresh(vehiculo_db)
        return vehiculo_db
    
    def eliminar_vehiculo(self, vehi_id: int) -> bool:
        # Usamos select() para encontrar el vehículo
        statement = select(Vehiculo).where(Vehiculo.vehi_id == vehi_id)
        vehiculo_db = self.db.exec(statement).first()

        if not vehiculo_db:
            return False  # Si no se encuentra el vehículo, no lo eliminamos

        self.db.delete(vehiculo_db)  # Eliminar el vehículo de la base de datos
        self.db.commit()  # Confirmamos los cambios
        return True  # Eliminación exitosa
