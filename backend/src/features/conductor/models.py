from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.core.db import Base


class Conductor(Base):
    __tablename__ = "conductor"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    cedula = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    registros = relationship("Registro", back_populates="conductor")