from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.database import Base

class TipoRegistro(Base):
    __tablename__ = "tipo_registro"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)

    registros = relationship("Registro", back_populates="tipo")