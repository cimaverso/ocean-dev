from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .modelo_registro import Registro  # Importar aquí para evitar problemas de referencia circular



class Vehiculo(SQLModel, table=True):
    __tablename__ = "vehiculo"
    vehi_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    vehi_placa: str = None

    registros: list["Registro"] = Relationship(back_populates="vehiculo")

class VehiculoCreate(SQLModel):
    vehi_placa: str = Field(..., max_length=10)

class VehiculoUpdate(SQLModel):
    vehi_placa: Optional[str] = Field(None, max_length=10)

class VehiculoResponse(SQLModel):
    vehi_id: int
    vehi_placa: str

    model_config = {"from_attributes": True}



