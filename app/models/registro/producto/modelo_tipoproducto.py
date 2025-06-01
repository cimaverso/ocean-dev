from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .modelo_producto import Producto  # Importar aquí para evitar problemas de referencia circular

class TipoProducto(SQLModel, table=True):
    __tablename__ = "tipo_producto"
    tprod_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    tprod_nombre: str

    productos: list["Producto"] = Relationship(back_populates="tipo_producto")


class TipoProductoResponse(SQLModel):
    tprod_id: int
    tprod_nombre: str

    model_config = {"from_attributes": True}