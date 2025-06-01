# services/proceso.py

from sqlmodel import Session, select
from app.models.registro.producto.modelo_procesoproducto import ProcesoProducto

class ProcesoProductoService:
    def __init__(self, db: Session):
        self.db = db

    def listar_procesos(self):
        statement = select(ProcesoProducto).order_by(ProcesoProducto.pp_id)
        return self.db.exec(statement).all()

   

   