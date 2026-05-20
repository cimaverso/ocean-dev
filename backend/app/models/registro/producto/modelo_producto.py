from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.registro.producto.modelo_tipoproducto import TipoProductoResponse
from app.models.registro.producto.modelo_procesoproducto import ProcesoProductoResponse
from app.models.registro.producto.modelo_unidadmedida import UnidadMedidaResponse


if TYPE_CHECKING:
    from app.models.registro.modelo_registro import Registro  # Importar aquí para evitar problemas de referencia circular
    from .modelo_producto import TipoProducto
    from .modelo_tipoproducto import ProcesoProducto
    from .modelo_unidadmedida import UnidadMedida


#Modelo producto
class Producto(SQLModel, table=True):
    __tablename__ = "producto"
    prod_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    prod_nombre: str 
    prod_idunidadmedida: int = Field(foreign_key="unidad_medida.um_id")
    prod_idtipoproducto: int = Field(foreign_key="tipo_producto.tprod_id", gt=0, lt=3)
    prod_codigo: Optional[str] = None
    prod_idprocesoproducto: int = Field(foreign_key="proceso_producto.pp_id", gt=0, lt=5)

    tipo_producto: 'TipoProducto' = Relationship(back_populates="productos")
    proceso_producto: 'ProcesoProducto' = Relationship(back_populates="productos")
    unidad_medida: 'UnidadMedida' = Relationship(back_populates="productos")
    registros: list["Registro"] = Relationship(back_populates="producto")



class ProductoCreate(SQLModel):
    prod_nombre: str
    prod_idunidadmedida: int 
    prod_idtipoproducto: int = Field(gt=0, lt=3)
    prod_codigo: Optional[str] = None
    prod_idprocesoproducto: int = Field(gt=0, lt=5)

class ProductoUpdate(SQLModel):
    prod_nombre: Optional[str] = None
    prod_idunidadmedida:Optional[int] = None
    prod_idtipoproducto: Optional[int] = None
    prod_codigo: Optional[str] = None
    prod_idprocesoproducto: Optional[int] = None

class ProductoResponse(SQLModel):
    prod_id: int 
    prod_nombre: str
    unidad_medida: UnidadMedidaResponse
    tipo_producto: TipoProductoResponse
    prod_codigo: Optional[str] = None
    proceso_producto: ProcesoProductoResponse

    model_config = {"from_attributes": True}

    
