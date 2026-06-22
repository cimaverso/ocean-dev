from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.core.db import Base


class Factura(Base):
    __tablename__ = "factura"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(String, nullable=False)
    registros = relationship("Registro", back_populates="factura")