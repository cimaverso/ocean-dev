# Aquí solo importas todos los modelos (esto es lo que "registra" las tablas)
from app.models.registro.modelo_registro import Registro
from app.models.historial.modelo_historial import Historial
from app.models.registro.modelo_tiporegistro import TipoRegistro
from app.models.registro.entidad.modelo_entidad import Entidad
from app.models.registro.entidad.modelo_tipoentidad import TipoEntidad
from app.models.registro.producto.modelo_producto import Producto
from app.models.registro.producto.modelo_tipoproducto import TipoProducto
from app.models.registro.producto.modelo_procesoproducto import ProcesoProducto
from app.models.registro.producto.modelo_unidadmedida import UnidadMedida
from app.models.registro.modelo_conductor import Conductor
from app.models.registro.modelo_vehiculo import Vehiculo
from app.models.registro.modelo_trailer import Trailer
from app.models.registro.modelo_comprador import Comprador
from app.models.registro.modelo_transportadora import Transportadora
from app.models.registro.modelo_factura import Factura
from app.models.registro.modelo_destino import Destino
from app.models.registro.modelo_origen import Origen
from app.models.registro.modelo_patio import Patio
from app.models.usuario.modelo_usuario import Usuario
from app.models.usuario.modelo_rol import Rol
from app.models.modelo_auth import TokenResponse, RefreshTokenResponse

