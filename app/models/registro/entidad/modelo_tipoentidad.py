from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .modelo_entidad import Entidad  # Importar aquí para evitar problemas de referencia circular

class TipoEntidad(SQLModel, table=True):
    __tablename__ = "tipo_entidad"
    tpent_id: int = Field(primary_key=True, index=True)
    tpent_nombre: str
    entidad: list["Entidad"] = Relationship(back_populates="tipo")


class TipoEntidadResponse(SQLModel):
    tpent_id: int
    tpent_nombre: str


    model_config = {"from_attributes": True}
