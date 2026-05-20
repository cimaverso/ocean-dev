from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .modelo_registro import Registro  # Importar aquí para evitar problemas de referencia circular


class Factura(SQLModel, table=True):
    __tablename__ = "factura"
    fac_id: int = Field(primary_key=True, index=True, alias="factura_id")
    fac_fecha: str 

    registros: list['Registro'] = Relationship(back_populates="factura")
  
class FacturaCreate(SQLModel):
    fac_fecha: str 
 
class FacturaUpdate(SQLModel):
    fac_fecha: Optional[str] =  None
   
class FacturaResponse(SQLModel):
    fac_id: int
    fac_fecha: str

    model_config = {"from_attributes": True}


