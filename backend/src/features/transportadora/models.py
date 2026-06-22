from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.core.db import Base


class Transportadora(Base):
    __tablename__ = "transportadora"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    ciudad = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    nit = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    codigo = Column(String, nullable=True)
    registros = relationship("Registro", back_populates="transportadora")