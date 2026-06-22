from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.core.db import Base


class UnidadMedida(Base):
    __tablename__ = "unidad_medida"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    productos = relationship("Producto", back_populates="unidad_medida")