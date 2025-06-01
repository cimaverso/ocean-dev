from typing import Optional, TYPE_CHECKING, List
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .modelo_registro import Registro  # Importar aquí para evitar problemas de referencia circular



class TipoRegistro(SQLModel, table=True):
    __tablename__ = "tipo_registro"
    tr_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    tr_nombre: str

    registros: List['Registro'] = Relationship(back_populates="tipo")

class TipoRegistroResponse(SQLModel):
    tr_id: int
    tr_nombre: str

    model_config = {"from_attributes": True}