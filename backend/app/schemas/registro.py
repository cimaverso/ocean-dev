from pydantic import BaseModel
from typing import Optional
from datetime import date, time
from app.schemas.tipo_registro import TipoRegistroResponse
from app.schemas.vehiculo import VehiculoResponse
from app.schemas.trailer import TrailerResponse
from app.schemas.conductor import ConductorResponse
from app.schemas.entidad import EntidadResponse
from app.schemas.producto import ProductoResponse
from app.schemas.comprador import CompradorResponse
from app.schemas.transportadora import TransportadoraResponse
from app.schemas.origen import OrigenResponse
from app.schemas.destino import DestinoResponse
from app.schemas.patio import PatioResponse
from app.schemas.factura import FacturaResponse

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