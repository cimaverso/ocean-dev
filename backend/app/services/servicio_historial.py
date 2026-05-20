from sqlmodel import Session, select, desc, or_
from sqlalchemy.orm import selectinload
from app.models.historial.modelo_historial import Historial
from datetime import date
from app.models.registro.modelo_registro import Registro
from app.models.usuario.modelo_usuario import Usuario
from typing import Optional
import pandas as pd
import io


class HistorialService:
    def __init__(self, db: Session):
        self.db = db

    def listar_historial(self):
        historial = (
            select(Historial).options(
                selectinload(Historial.registro),
                selectinload(Historial.usuario),
                
            )
            .order_by(
                desc(Historial.his_fecha), 
                desc(Historial.his_hora),
            )
        )
        results = self.db.exec(historial)
        return results.all()
    
    def exportar_historial(self, consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None):
        # Consultar todos los vehículos
        historial = select(Historial).order_by(Historial.his_id)


        if fecha_inicio and fecha_fin:
            historial = historial.where(Historial.his_fecha.between(fecha_inicio, fecha_fin))
        elif fecha_inicio:
            historial = historial.where(Historial.his_fecha >= fecha_inicio)
        elif fecha_fin:
            historial = historial.where(Historial.his_fecha <= fecha_fin)
       

        if consulta:
            consulta = consulta.lower()
            historial = historial.where(
                or_(
                    historial.usuario.has(Usuario.usuario_nombre.ilike(f"%{consulta}%")),
                    historial.usuario.has(Usuario.rol.rol_nombre.ilike(f"%{consulta}%")),
                    historial.registro.has(Registro.tipo.tr_nombre.ilike(f"%{consulta}%")),
                    historial.registro.has(Registro.reg_consecutivo.ilike(f"%{consulta}%")),
                    historial.his_accion.ilike(f"%{consulta}%")
                )
            )

        result = self.db.execute(historial)
        historial = result.scalars().all()  # Esto obtiene los registros reales
      

        data = [
            {

                "Tipo": his.registro.tipo.tr_nombre if his.registro else "N/A",
                "Registro": his.registro.reg_consecutivo if his.registro else "N/A",
                "Accion": his.his_accion,
                "Fecha": his.his_fecha,
                "Hora": his.his_hora,
                "Usuario": his.usuario.usuario_nombre if his.usuario else "N/A",
                "Rol": his.usuario.rol.rol_nombre if his.usuario and his.usuario.rol else "N/A",
            }
            for his in historial
        ]

        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = "Historial"
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