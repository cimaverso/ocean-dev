from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.database import Base

class TipoProducto(Base):
    __tablename__ = "tipo_producto"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)

    productos = relationship("Producto", back_populates="tipo_producto")