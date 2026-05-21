from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, desc, or_
from app.models.historial import Historial
from app.models.usuario import Usuario
from datetime import date
from typing import Optional
import pandas as pd
import io


class HistorialService:
    def __init__(self, db: Session):
        self.db = db

    def listar_historial(self):
        return self.db.execute(
            select(Historial)
            .options(
                selectinload(Historial.registro),
                selectinload(Historial.usuario),
            )
            .order_by(desc(Historial.fecha), desc(Historial.hora))
        ).scalars().all()

    def exportar_historial(self, consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None):
        query = select(Historial).order_by(Historial.id)

        if fecha_inicio and fecha_fin:
            query = query.where(Historial.fecha.between(fecha_inicio, fecha_fin))
        elif fecha_inicio:
            query = query.where(Historial.fecha >= fecha_inicio)
        elif fecha_fin:
            query = query.where(Historial.fecha <= fecha_fin)

        if consulta:
            consulta = consulta.lower()
            query = query.where(
                or_(
                    Historial.usuario.has(Usuario.nombre.ilike(f"%{consulta}%")),
                    Historial.accion.ilike(f"%{consulta}%")
                )
            )

        historial = self.db.execute(query).scalars().all()

        data = [
            {
                "Tipo": h.registro.tipo.nombre if h.registro else "N/A",
                "Registro": h.registro.consecutivo if h.registro else "N/A",
                "Accion": h.accion,
                "Fecha": h.fecha,
                "Hora": h.hora,
                "Usuario": h.usuario.nombre if h.usuario else "N/A",
                "Rol": h.usuario.rol.nombre if h.usuario and h.usuario.rol else "N/A",
            }
            for h in historial
        ]

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Historial")
            workbook = writer.book
            sheet = workbook["Historial"]
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