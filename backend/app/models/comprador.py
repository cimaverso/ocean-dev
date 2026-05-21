from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.database import Base

class Comprador(Base):
    __tablename__ = "comprador"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    nit = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    codigo = Column(String, nullable=True)

    registros = relationship("Registro", back_populates="comprador")