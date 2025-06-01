from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .modelo_producto import Producto  # Importar aquí para evitar problemas de referencia circular


class UnidadMedida(SQLModel, table=True):
    __tablename__ = "unidad_medida"
    um_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    um_nombre: str

    productos: list["Producto"] = Relationship(back_populates="unidad_medida")


class UnidadMedidaCreate(SQLModel):
    um_nombre: str

class UnidadMedidaUpdate(SQLModel):
    um_nombre: Optional[str]

class UnidadMedidaResponse(SQLModel):
    um_id: int
    um_nombre: str

    model_config = {"from_attributes": True}