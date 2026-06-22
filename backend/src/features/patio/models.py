from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.core.db import Base


class Patio(Base):
    __tablename__ = "patio"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    codigo = Column(String, nullable=True)
    registros = relationship("Registro", back_populates="patio")