from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from typing import Optional
import pandas as pd
import io

from src.features.entidad.models import Entidad
from src.features.entidad.schemas import EntidadCreate, EntidadUpdate


class EntidadService:
    def __init__(self, db: Session):
        self.db = db

    def listar_entidad(self, tipo: int) -> list[Entidad]:
        return self.db.execute(
            select(Entidad)
            .where(Entidad.tipo_id == tipo)
            .options(selectinload(Entidad.tipo))
        ).scalars().all()

    def exportar_entidades(self, tipo_entidad: int, consulta: Optional[str] = None) -> io.BytesIO:
        query = select(Entidad).where(Entidad.tipo_id == tipo_entidad)
        if consulta:
            query = query.where(
                Entidad.codigo.ilike(f"%{consulta}%") |
                Entidad.nombre.ilike(f"%{consulta}%") |
                Entidad.nit.ilike(f"%{consulta}%") |
                Entidad.telefono.ilike(f"%{consulta}%")
            )
        entidades = self.db.execute(query).scalars().all()
        data = [{"Codigo": e.codigo, "Entidad": e.nombre, "NIT": e.nit, "Telefono": e.telefono} for e in entidades]
        df = pd.DataFrame(data)
        output = io.BytesIO()
        sheet_name = {1: "Clientes", 2: "Proveedores", 3: "Terceros"}.get(tipo_entidad, "Entidad")
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            sheet = writer.book[sheet_name]
            for col in sheet.columns:
                max_length = max((len(str(cell.value)) for cell in col if cell.value), default=0)
                sheet.column_dimensions[col[0].column_letter].width = max_length + 2
        output.seek(0)
        return output

    def crear_entidad(self, data: EntidadCreate) -> Entidad:
        nueva = Entidad(**data.model_dump())
        self.db.add(nueva)
        self.db.commit()
        self.db.refresh(nueva)
        return self.db.execute(
            select(Entidad).options(selectinload(Entidad.tipo)).where(Entidad.id == nueva.id)
        ).scalar_one_or_none()

    def actualizar_entidad(self, id: int, data: EntidadUpdate) -> Entidad | None:
        entidad = self.db.execute(select(Entidad).where(Entidad.id == id)).scalar_one_or_none()
        if not entidad:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(entidad, key, value)
        self.db.commit()
        self.db.refresh(entidad)
        return entidad