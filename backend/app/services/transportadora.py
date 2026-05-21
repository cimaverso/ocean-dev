from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.transportadora import Transportadora
from app.schemas.transportadora import TransportadoraCreate, TransportadoraUpdate
from typing import Optional
import pandas as pd
import io


class TransportadoraService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_transportadoras(self):
        return self.db.execute(select(Transportadora).order_by(Transportadora.id)).scalars().all()

    def exportar_transportadoras(self, consulta: Optional[str] = None):
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

        data = [
            {
                "Codigo": t.codigo,
                "Transportadora": t.nombre,
                "Ciudad": t.ciudad,
                "Nit": t.nit,
                "Telefono": t.telefono,
                "Direccion": t.direccion,
            }
            for t in transportadoras
        ]

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Transportadoras")
            workbook = writer.book
            sheet = workbook["Transportadoras"]
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

    def crear_transportadora(self, transportadora_data: TransportadoraCreate):
        nueva_transportadora = Transportadora(**transportadora_data.model_dump())
        self.db.add(nueva_transportadora)
        self.db.commit()
        self.db.refresh(nueva_transportadora)
        return nueva_transportadora

    def actualizar_transportadora(self, id: int, transportadora_data: TransportadoraUpdate):
        transportadora_db = self.db.execute(
            select(Transportadora).where(Transportadora.id == id)
        ).scalar_one_or_none()

        if not transportadora_db:
            return None

        for key, value in transportadora_data.model_dump(exclude_unset=True).items():
            setattr(transportadora_db, key, value)

        self.db.commit()
        self.db.refresh(transportadora_db)
        return transportadora_db

    