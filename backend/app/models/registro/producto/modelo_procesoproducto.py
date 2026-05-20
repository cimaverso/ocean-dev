
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .modelo_producto import Producto  # Importar aquí para evitar problemas de referencia circular


class ProcesoProducto(SQLModel, table=True):
    __tablename__ = "proceso_producto"
    pp_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    pp_nombre: str

    productos: list["Producto"] = Relationship(back_populates="proceso_producto")


class ProcesoProductoResponse(SQLModel):
    pp_id: int
    pp_nombre: str

    model_config = {"from_attributes": True}