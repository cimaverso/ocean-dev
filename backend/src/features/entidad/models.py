from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.core.db import Base


class TipoEntidad(Base):
    __tablename__ = "tipo_entidad"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    entidades = relationship("Entidad", back_populates="tipo")


class Entidad(Base):
    __tablename__ = "entidad"

    id = Column(Integer, primary_key=True, index=True)
    tipo_id = Column(Integer, ForeignKey("tipo_entidad.id"), nullable=False)
    nombre = Column(String, nullable=False)
    nit = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    codigo = Column(String, nullable=True)
    tipo = relationship("TipoEntidad", back_populates="entidades")
    registros = relationship("Registro", back_populates="entidad")