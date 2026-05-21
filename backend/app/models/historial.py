from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

class Historial(Base):
    __tablename__ = "historial"

    id = Column(Integer, primary_key=True, index=True)
    accion = Column(String, nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    registro_id = Column(Integer, ForeignKey("registro.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="historial")
    registro = relationship("Registro", back_populates="historial")