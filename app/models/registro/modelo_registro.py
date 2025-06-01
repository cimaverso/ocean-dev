
from typing import Optional, TYPE_CHECKING, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date, time

from app.models.registro.producto.modelo_producto import ProductoResponse
from app.models.registro.entidad.modelo_entidad import EntidadResponse
from app.models.registro.modelo_tiporegistro import TipoRegistroResponse
from app.models.registro.modelo_conductor import ConductorResponse
from app.models.registro.modelo_vehiculo import VehiculoResponse
from app.models.registro.modelo_trailer import TrailerResponse
from app.models.registro.modelo_comprador import CompradorResponse
from app.models.registro.modelo_transportadora import TransportadoraResponse
from app.models.registro.modelo_origen import OrigenResponse
from app.models.registro.modelo_destino import DestinoResponse
from app.models.registro.modelo_patio import PatioResponse
from app.models.registro.modelo_factura import FacturaResponse



if TYPE_CHECKING:

    from .modelo_vehiculo import Vehiculo
    from .modelo_trailer import Trailer
    from .modelo_conductor import Conductor
    from app.models.registro.entidad.modelo_entidad import Entidad
    from app.models.registro.producto.modelo_producto import Producto
    from .modelo_comprador import Comprador
    from .modelo_transportadora import Transportadora
    from .modelo_origen import Origen
    from .modelo_destino import Destino
    from .modelo_patio import Patio
    from .modelo_factura import Factura
    from .modelo_tiporegistro import TipoRegistro  
    from app.models.historial.modelo_historial import Historial




class Registro(SQLModel, table=True):
    __tablename__ = "registro"
    reg_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    reg_idtipo: int = Field(foreign_key="tipo_registro.tr_id")

    reg_fechaentrada: Optional[date] = Field(default=None)
    reg_horaentrada: Optional[time] = Field(default=None)
    reg_fechasalida: Optional[date] = Field(default=None)
    reg_horasalida: Optional[time] = Field(default=None)


    reg_idvehiculo: Optional[int] = Field(default=None, foreign_key="vehiculo.vehi_id")
    reg_idtrailer: Optional[int] = Field(default=None, foreign_key="trailer.trai_id")
    reg_idconductor: Optional[int] = Field(default=None, foreign_key="conductor.conduct_id")
    reg_identidad: Optional[int] = Field(default=None, foreign_key="entidad.ent_id")
    reg_idproducto: Optional[int] = Field(default=None, foreign_key="producto.prod_id")
    reg_cantidad: Optional[int] = Field(default=None)
    reg_idcomprador: Optional[int] = Field(default=None, foreign_key="comprador.comp_id")
    reg_idtransportadora: Optional[int] = Field(default=None, foreign_key="transportadora.trans_id")
    reg_orden: Optional[str] =  Field(default=None)
    reg_precinto: Optional[str] = Field(default=None)

    reg_idorigen: Optional[int] = Field(default=None, foreign_key="origen.ori_id")
    reg_iddestino: Optional[int] = Field(default=None, foreign_key="destino.dest_id")
    reg_idpatio: Optional[int] = Field(default=None, foreign_key="patio.pat_id")
    reg_idfactura: Optional[int] = Field(default=None, foreign_key="factura.fac_id")

    reg_pesobruto: Optional[int] = Field(default=None)
    reg_pesotara: Optional[int] = Field(default=None)
    reg_pesoneto: Optional[int] = Field(default=None)
    
    reg_estado: Optional[int] = Field(default=None)
    reg_acceso: Optional[int] = Field(default=None)
    reg_observaciones: Optional[str] = Field(default=None)
    reg_consecutivo: Optional[int] = Field(default=None)
    reg_tiquete: Optional[int] = Field(default=None)


    # Relaciones
    historial: List['Historial'] = Relationship(back_populates="registro")
    
    tipo: 'TipoRegistro' = Relationship(back_populates="registros")
    vehiculo: 'Vehiculo' = Relationship(back_populates="registros")   
    trailer: 'Trailer' = Relationship(back_populates="registros")
    conductor: 'Conductor' = Relationship(back_populates="registros")
    entidad: 'Entidad' = Relationship(back_populates="registros")
    producto: 'Producto' = Relationship(back_populates="registros")
    comprador: 'Comprador' = Relationship(back_populates="registros")
    transportadora: 'Transportadora' = Relationship(back_populates="registros")
    origen: 'Origen' = Relationship(back_populates="registros")
    destino: 'Destino' = Relationship(back_populates="registros")
    patio: 'Patio' = Relationship(back_populates="registros")
    factura: 'Factura' = Relationship(back_populates="registros")

   
    
    

class RegistroCreate(SQLModel):
    reg_idtipo: int
    reg_fechaentrada: date
    reg_horaentrada: time
    reg_idtrailer: Optional[int] = None
    reg_idvehiculo: Optional[int] = None
    reg_idconductor: Optional[int] = None
    reg_identidad: Optional[int] = None
    reg_idproducto: Optional[int] = None
    reg_cantidad: Optional[int] = None
    reg_idcomprador: Optional[int] = None
    reg_iddestino: Optional[int] = None
    reg_idpatio: Optional[int] = None
    reg_idorigen: Optional[int] = None
    reg_idfactura: Optional[int] = None
    reg_idtransportadora: Optional[int] = None
    reg_orden: Optional[str] = None
    reg_precinto: Optional[str] = None
    reg_pesobruto: Optional[int] = None
    reg_pesotara: Optional[int] = None
    reg_observaciones: Optional[str] = None
    reg_consecutivo: Optional[int] = None
    


class RegistroUpdate(SQLModel):
    reg_fechaentrada: Optional[date] = None
    reg_horaentrada: Optional[time] = None
    reg_fechasalida: Optional[date] = None
    reg_horasalida: Optional[time] = None
    reg_idtrailer: Optional[int] = None
    reg_idvehiculo: Optional[int] = None
    reg_idconductor: Optional[int] = None
    reg_identidad: Optional[int] = None
    reg_idproducto: Optional[int] = None
    reg_cantidad: Optional[int] = None
    reg_idcomprador: Optional[int] = None
    reg_iddestino: Optional[int] = None
    reg_idpatio: Optional[int] = None
    reg_idorigen: Optional[int] = None
    reg_idfactura: Optional[int] = None
    reg_idtransportadora: Optional[int] = None
    reg_orden: Optional[str] = None
    reg_precinto: Optional[str] = None
    reg_pesobruto: Optional[int] = None
    reg_pesotara: Optional[int] = None
    reg_pesoneto: Optional[int] = None
    reg_observaciones: Optional[str] = None
    reg_tiquete: Optional[int] = None

class RegistroConsecutivo(SQLModel):
    reg_id: int

class RegistroResponse(SQLModel):
    reg_id: int
    tipo: TipoRegistroResponse
    reg_fechaentrada: date
    reg_horaentrada: time
    reg_fechasalida: Optional[date] = None
    reg_horasalida: Optional[time] = None
    trailer: Optional[TrailerResponse] = None
    vehiculo: Optional[VehiculoResponse] = None
    conductor: Optional[ConductorResponse] = None
    entidad: Optional[EntidadResponse] = None
    producto: Optional[ProductoResponse] = None
    reg_cantidad: Optional[int] = None
    comprador: Optional[CompradorResponse] = None
    transportadora: Optional[TransportadoraResponse] = None
    reg_orden: Optional[str] = None
    reg_precinto: Optional[str] = None
    origen: Optional[OrigenResponse] = None
    destino: Optional[DestinoResponse] = None
    patio: Optional[PatioResponse] = None
    reg_pesobruto: Optional[int] = None
    reg_pesotara: Optional[int] = None
    reg_pesoneto: Optional[int] = None
    factura: Optional[FacturaResponse] = None
    reg_estado: Optional[int] = None
    reg_acceso: Optional[int] = None
    reg_observaciones: Optional[str] = None
    reg_consecutivo: Optional[int] = None
    reg_tiquete: Optional[int] = None
  

    model_config = {"from_attributes": True}


