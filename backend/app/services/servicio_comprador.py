from sqlmodel import Session, select
from app.models.registro.modelo_comprador import Comprador, CompradorCreate, CompradorUpdate
import pandas as pd
import io
from typing import Optional


#Comprador 

class CompradorService:
    def __init__(self, db: Session):
        self.db = db

    def listar_compradores(self):
        # Usamos 'select' para hacer la consulta de los compradores, y luego ordenamos por 'comp_id'
        statement = select(Comprador).order_by(Comprador.comp_id)
        return self.db.exec(statement).all()

    def exportar_compradores(self, consulta: Optional[str] = None):
        # Consultar todos los vehículos
        compradores = select(Comprador).order_by(Comprador.comp_id)
        
        if consulta:
            compradores = compradores.where(
                (
                    Comprador.comp_codigo.ilike(f"%{consulta}%"), 
                    Comprador.comp_nombre.ilike(f"%{consulta}%"),
                    Comprador.comp_nit.ilike(f"%{consulta}%"),
                    Comprador.comp_telefono.ilike(f"%{consulta}%"),
                    
                )
            )
        result = self.db.execute(compradores)
        compradores = result.scalars().all()

        # Preparar los datos para el DataFrame
        data = [
            {
                "Codigo": comprador.comp_codigo,
                "Comprador": comprador.comp_nombre,
                "Nit": comprador.comp_nit,
                "Telefono": comprador.comp_telefono,
                
            }
            for comprador in compradores
        ]

        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = "Compradores"
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

    def crear_comprador(self, comprador_data: CompradorCreate):
        # Creamos el nuevo comprador a partir del esquema y lo agregamos a la sesión
        nuevo_comprador = Comprador(**comprador_data.dict())
        self.db.add(nuevo_comprador)
        self.db.commit()  # Confirmamos los cambios en la base de datos
        self.db.refresh(nuevo_comprador)  # Recargamos los datos del comprador recién creado

        return nuevo_comprador

    def actualizar_comprador(self, comp_id: int, comprador_data: CompradorUpdate):
        # Usamos 'select' para obtener al comprador existente basado en su 'comp_id'
        statement = select(Comprador).where(Comprador.comp_id == comp_id)
        comprador_db = self.db.exec(statement).first()

        if not comprador_db:
            return None  # Si no se encuentra el comprador, devolvemos None

        # Actualizamos los campos del comprador utilizando los datos proporcionados
        update_data = comprador_data.dict(exclude_unset=True)  # Excluimos los campos no proporcionados
        for key, value in update_data.items():
            setattr(comprador_db, key, value)

        self.db.commit()  # Confirmamos los cambios en la base de datos
        self.db.refresh(comprador_db)  # Recargamos los datos actualizados

        return comprador_db

    def eliminar_comprador(self, comp_id: int):
        # Usamos 'select' para obtener al comprador a eliminar
        statement = select(Comprador).where(Comprador.comp_id == comp_id)
        comprador_db = self.db.exec(statement).first()

        if comprador_db:
            self.db.delete(comprador_db)  # Marcamos el comprador para eliminarlo
            self.db.commit()  # Confirmamos la eliminación en la base de datos
            return True  # Retornamos 'True' si la eliminación fue exitosa
        return False  # Retornamos 'False' si no se encontró el comprador

