from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.database import Base

class Vehiculo(Base):
    __tablename__ = "vehiculo"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), nullable=False)

    registros = relationship("Registro", back_populates="vehiculo")