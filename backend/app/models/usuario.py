from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, nullable=True)
    clave = Column(String, nullable=False)
    rol_id = Column(Integer, ForeignKey("rol.id"), nullable=False)

    rol = relationship("Rol", back_populates="usuarios")
    historial = relationship("Historial", back_populates="usuario")