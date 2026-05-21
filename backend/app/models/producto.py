from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

class Producto(Base):
    __tablename__ = "producto"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    codigo = Column(String, nullable=True)
    unidad_medida_id = Column(Integer, ForeignKey("unidad_medida.id"), nullable=False)
    tipo_producto_id = Column(Integer, ForeignKey("tipo_producto.id"), nullable=False)
    proceso_producto_id = Column(Integer, ForeignKey("proceso_producto.id"), nullable=False)

    unidad_medida = relationship("UnidadMedida", back_populates="productos")
    tipo_producto = relationship("TipoProducto", back_populates="productos")
    proceso_producto = relationship("ProcesoProducto", back_populates="productos")
    registros = relationship("Registro", back_populates="producto")