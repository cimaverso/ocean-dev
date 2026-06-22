from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
import pandas as pd
import io

from src.features.transportadora.models import Transportadora
from src.features.transportadora.schemas import TransportadoraCreate, TransportadoraUpdate


class TransportadoraService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_transportadoras(self) -> list[Transportadora]:
        return self.db.execute(select(Transportadora).order_by(Transportadora.id)).scalars().all()

    def exportar_transportadoras(self, consulta: Optional[str] = None) -> io.BytesIO:
        query = select(Transportadora).order_by(Transportadora.id)
        if consulta:
            query = query.where(
                Transportadora.codigo.ilike(f"%{consulta}%") |
                Transportadora.nombre.ilike(f"%{consulta}%") |
                Transportadora.ciudad.ilike(f"%{consulta}%") |
                Transportadora.nit.ilike(f"%{consulta}%") |
                Transportadora.telefono.ilike(f"%{consulta}%") |
                Transportadora.direccion.ilike(f"%{consulta}%")
            )
        transportadoras = self.db.execute(query).scalars().all()
        data = [{
            "Codigo": t.codigo, "Transportadora": t.nombre,
            "Ciudad": t.ciudad, "Nit": t.nit,
            "Telefono": t.telefono, "Direccion": t.direccion,
        } for t in transportadoras]
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Transportadoras")
            sheet = writer.book["Transportadoras"]
            for col in sheet.columns:
                max_length = max((len(str(cell.value)) for cell in col if cell.value), default=0)
                sheet.column_dimensions[col[0].column_letter].width = max_length + 2
        output.seek(0)
        return output

    def crear_transportadora(self, data: TransportadoraCreate) -> Transportadora:
        nueva = Transportadora(**data.model_dump())
        self.db.add(nueva)
        self.db.commit()
        self.db.refresh(nueva)
        return nueva

    def actualizar_transportadora(self, id: int, data: TransportadoraUpdate) -> Transportadora | None:
        t = self.db.execute(select(Transportadora).where(Transportadora.id == id)).scalar_one_or_none()
        if not t:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(t, key, value)
        self.db.commit()
        self.db.refresh(t)
        return t