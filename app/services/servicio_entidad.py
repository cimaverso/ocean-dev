# services/entidad.py

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.models.registro.entidad.modelo_entidad import Entidad, EntidadCreate, EntidadUpdate
import io
import pandas as pd
from sqlalchemy.orm import Session
from app.models import *
from typing import Optional



class EntidadService:
    def __init__(self, db: Session):
        self.db = db

    
    def listar_entidad(self, tipo: int):
        # Usamos selectinload para cargar la relación 'tipo' de Entidad (TipoEntidad)
        statement = select(Entidad).where(Entidad.ent_idtipoentidad == tipo).options(
            selectinload(Entidad.tipo)  # Esto carga la relación 'tipo' de Entidad (TipoEntidad)
        )
        results = self.db.exec(statement)
        return results.all()

        #
    
    def exportar_entidades(self, tipo_entidad: int, consulta: Optional[str] = None):
        """Exporta una entidad (cliente, proveedor, tercero) a un archivo Excel"""

        # Filtrar por tipo de entidad (clientes=1, proveedores=2, terceros=3) y consulta
        entidades = select(Entidad).where(Entidad.ent_idtipoentidad == tipo_entidad)
        
        if consulta:
            entidades = entidades.where(
                (
                    Entidad.ent_codigo.ilike(f"%{consulta}%") |
                    Entidad.ent_nombre.ilike(f"%{consulta}%") |
                    Entidad.ent_nit.ilike(f"%{consulta}%") |
                    Entidad.ent_telefono.ilike(f"%{consulta}%")
                )
            )
        
        result = self.db.execute(entidades)
        entidades = result.scalars().all()  # Utiliza scalars() para obtener las instancias

        # Convertir a DataFrame
        data = [
            {
                "Codigo": entidad.ent_codigo, 
                "Entidad": entidad.ent_nombre, 
                "NIT": entidad.ent_nit if entidad else None,
                "Telefono": entidad.ent_telefono if entidad else None
            }
            for entidad in entidades
        ]
        
        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = {1: "Clientes", 2: "Proveedores", 3: "Terceros"}.get(tipo_entidad, "Entidad")
            column_name = {1: "Cliente", 2: "Proveedor", 3: "Tercero"}.get(tipo_entidad, "Entidad")
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            # Obtener el libro y la hoja activa
            workbook = writer.book
            sheet = workbook[sheet_name]

            sheet.cell(row=1, column=2, value=column_name)  # Cambiar el nombre de la columna

            
            # Ajustar el ancho de las columnas al contenido
            for col in sheet.columns:
                max_length = 0
                column = col[0].column_letter  # Obtiene la letra de la columna
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)  # Añadir espacio extra
                sheet.column_dimensions[column].width = adjusted_width
        
        output.seek(0)

        return output

    def crear_entidad(self, entidad_data: EntidadCreate):
        nueva_entidad = Entidad(**entidad_data.dict())

        self.db.add(nueva_entidad)
        self.db.commit()
        self.db.refresh(nueva_entidad)

        statement = select(Entidad).options(selectinload(Entidad.tipo)).where(Entidad.ent_id == nueva_entidad.ent_id)
        return self.db.exec(statement).first()

    def actualizar_entidad(self, ent_id: int, entidad_data: EntidadUpdate):
        statement = select(Entidad).where(Entidad.ent_id == ent_id)
        entidad_db = self.db.exec(statement).first()
        
        if not entidad_db:
            return None  # Si la entidad no existe, devolvemos None

        update_data = entidad_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entidad_db, key, value)

        self.db.commit()
        self.db.refresh(entidad_db)

        return entidad_db

    def eliminar_entidad(self, ent_id: int) -> bool:
        statement = select(Entidad).where(Entidad.ent_id == ent_id)
        entidad_db = self.db.exec(statement).first()
        
        if not entidad_db:
            return False
        
        self.db.delete(entidad_db)
        self.db.commit()

        return True
