from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.database import Base

class Trailer(Base):
    __tablename__ = "trailer"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String, nullable=False)

    registros = relationship("Registro", back_populates="trailer")