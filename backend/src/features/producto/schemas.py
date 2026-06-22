from pydantic import BaseModel
from typing import Optional
from src.features.medida.schemas import UnidadMedidaResponse


class TipoProductoResponse(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}


class ProcesoProductoResponse(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}


class ProductoCreate(BaseModel):
    nombre: str
    codigo: Optional[str] = None
    unidad_medida_id: int
    tipo_producto_id: int
    proceso_producto_id: int


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    unidad_medida_id: Optional[int] = None
    tipo_producto_id: Optional[int] = None
    proceso_producto_id: Optional[int] = None


class ProductoResponse(BaseModel):
    id: int
    nombre: str
    codigo: Optional[str] = None
    unidad_medida: UnidadMedidaResponse
    tipo_producto: TipoProductoResponse
    proceso_producto: ProcesoProductoResponse

    model_config = {"from_attributes": True}