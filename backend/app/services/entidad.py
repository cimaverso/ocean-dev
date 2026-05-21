from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.models.entidad import Entidad
from app.schemas.entidad import EntidadCreate, EntidadUpdate
import pandas as pd
import io
from typing import Optional


class EntidadService:
    def __init__(self, db: Session):
        self.db = db

    def listar_entidad(self, tipo: int):
        return self.db.execute(
            select(Entidad)
            .where(Entidad.tipo_id == tipo)
            .options(selectinload(Entidad.tipo))
        ).scalars().all()

    def exportar_entidades(self, tipo_entidad: int, consulta: Optional[str] = None):
        query = select(Entidad).where(Entidad.tipo_id == tipo_entidad)

        if consulta:
            query = query.where(
                Entidad.codigo.ilike(f"%{consulta}%") |
                Entidad.nombre.ilike(f"%{consulta}%") |
                Entidad.nit.ilike(f"%{consulta}%") |
                Entidad.telefono.ilike(f"%{consulta}%")
            )

        entidades = self.db.execute(query).scalars().all()

        data = [
            {
                "Codigo": e.codigo,
                "Entidad": e.nombre,
                "NIT": e.nit,
                "Telefono": e.telefono,
            }
            for e in entidades
        ]

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = {1: "Clientes", 2: "Proveedores", 3: "Terceros"}.get(tipo_entidad, "Entidad")
            column_name = {1: "Cliente", 2: "Proveedor", 3: "Tercero"}.get(tipo_entidad, "Entidad")
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            workbook = writer.book
            sheet = workbook[sheet_name]
            sheet.cell(row=1, column=2, value=column_name)
            for col in sheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value and len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except Exception:
                        pass
                sheet.column_dimensions[column].width = max_length + 2

        output.seek(0)
        return output

    def crear_entidad(self, entidad_data: EntidadCreate):
        nueva_entidad = Entidad(**entidad_data.model_dump())
        self.db.add(nueva_entidad)
        self.db.commit()
        self.db.refresh(nueva_entidad)

        return self.db.execute(
            select(Entidad).options(selectinload(Entidad.tipo)).where(Entidad.id == nueva_entidad.id)
        ).scalar_one_or_none()

    def actualizar_entidad(self, id: int, entidad_data: EntidadUpdate):
        entidad_db = self.db.execute(
            select(Entidad).where(Entidad.id == id)
        ).scalar_one_or_none()

        if not entidad_db:
            return None

        for key, value in entidad_data.model_dump(exclude_unset=True).items():
            setattr(entidad_db, key, value)

        self.db.commit()
        self.db.refresh(entidad_db)
        return entidad_db

    