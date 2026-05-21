from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.database import Base

class TipoEntidad(Base):
    __tablename__ = "tipo_entidad"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)

    entidades = relationship("Entidad", back_populates="tipo")