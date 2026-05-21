from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.proceso_producto import ProcesoProducto


class ProcesoProductoService:
    def __init__(self, db: Session):
        self.db = db

    def listar_procesos(self):
        return self.db.execute(select(ProcesoProducto).order_by(ProcesoProducto.id)).scalars().all()