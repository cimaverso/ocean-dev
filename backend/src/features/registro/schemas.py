from pydantic import BaseModel
from typing import Optional
from datetime import date, time

from src.features.vehiculo.schemas import VehiculoResponse
from src.features.trailer.schemas import TrailerResponse
from src.features.conductor.schemas import ConductorResponse
from src.features.entidad.schemas import EntidadResponse
from src.features.producto.schemas import ProductoResponse
from src.features.comprador.schemas import CompradorResponse
from src.features.transportadora.schemas import TransportadoraResponse
from src.features.origen.schemas import OrigenResponse
from src.features.destino.schemas import DestinoResponse
from src.features.patio.schemas import PatioResponse
from src.features.factura.schemas import FacturaResponse


class TipoRegistroResponse(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}


class RegistroCreate(BaseModel):
    tipo_id: int
    fecha_entrada: date
    hora_entrada: time
    vehiculo_id: Optional[int] = None
    trailer_id: Optional[int] = None
    conductor_id: Optional[int] = None
    entidad_id: Optional[int] = None
    producto_id: Optional[int] = None
    cantidad: Optional[int] = None
    comprador_id: Optional[int] = None
    destino_id: Optional[int] = None
    patio_id: Optional[int] = None
    origen_id: Optional[int] = None
    factura_id: Optional[int] = None
    transportadora_id: Optional[int] = None
    orden: Optional[str] = None
    precinto: Optional[str] = None
    peso_bruto: Optional[int] = None
    peso_tara: Optional[int] = None
    observaciones: Optional[str] = None
    consecutivo: Optional[int] = None


class RegistroUpdate(BaseModel):
    fecha_entrada: Optional[date] = None
    hora_entrada: Optional[time] = None
    fecha_salida: Optional[date] = None
    hora_salida: Optional[time] = None
    vehiculo_id: Optional[int] = None
    trailer_id: Optional[int] = None
    conductor_id: Optional[int] = None
    entidad_id: Optional[int] = None
    producto_id: Optional[int] = None
    cantidad: Optional[int] = None
    comprador_id: Optional[int] = None
    destino_id: Optional[int] = None
    patio_id: Optional[int] = None
    origen_id: Optional[int] = None
    factura_id: Optional[int] = None
    transportadora_id: Optional[int] = None
    orden: Optional[str] = None
    precinto: Optional[str] = None
    peso_bruto: Optional[int] = None
    peso_tara: Optional[int] = None
    peso_neto: Optional[int] = None
    observaciones: Optional[str] = None
    tiquete: Optional[int] = None


class RegistroResponse(BaseModel):
    id: int
    tipo: TipoRegistroResponse
    fecha_entrada: date
    hora_entrada: time
    fecha_salida: Optional[date] = None
    hora_salida: Optional[time] = None
    vehiculo: Optional[VehiculoResponse] = None
    trailer: Optional[TrailerResponse] = None
    conductor: Optional[ConductorResponse] = None
    entidad: Optional[EntidadResponse] = None
    producto: Optional[ProductoResponse] = None
    cantidad: Optional[int] = None
    comprador: Optional[CompradorResponse] = None
    transportadora: Optional[TransportadoraResponse] = None
    orden: Optional[str] = None
    precinto: Optional[str] = None
    origen: Optional[OrigenResponse] = None
    destino: Optional[DestinoResponse] = None
    patio: Optional[PatioResponse] = None
    peso_bruto: Optional[int] = None
    peso_tara: Optional[int] = None
    peso_neto: Optional[int] = None
    factura: Optional[FacturaResponse] = None
    estado: Optional[int] = None
    observaciones: Optional[str] = None
    consecutivo: Optional[int] = None
    tiquete: Optional[int] = None

    model_config = {"from_attributes": True}