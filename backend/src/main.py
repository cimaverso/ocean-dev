from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta

from src.core.db import engine
from src.features.auth.controller import AuthController, UsuarioController
from src.features.comprador.controller import CompradorController
from src.features.conductor.controller import ConductorController
from src.features.vehiculo.controller import VehiculoController
from src.features.trailer.controller import TrailerController
from src.features.destino.controller import DestinoController
from src.features.origen.controller import OrigenController
from src.features.patio.controller import PatioController
from src.features.entidad.controller import EntidadController
from src.features.medida.controller import MedidaController
from src.features.producto.controller import ProductoController
from src.features.transportadora.controller import TransportadoraController
from src.features.factura.controller import FacturaController
from src.features.registro.controller import RegistroController
from src.features.historial.controller import HistorialController

scheduler = BackgroundScheduler()

def eliminar_registros_viejos() -> None:
    from src.features.historial.models import Historial
    with Session(engine) as session:
        limite = datetime.utcnow() - timedelta(days=7)
        historial = session.execute(
            select(Historial).where(Historial.fecha < limite)
        ).scalars().all()
        for h in historial:
            session.delete(h)
        session.commit()
        print(f"✅ Se eliminaron {len(historial)} registros.")

def on_startup() -> None:
    scheduler.add_job(eliminar_registros_viejos, trigger="cron", day=30, hour=0, minute=0)
    scheduler.start()

cors_config = CORSConfig(
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app = Litestar(
    route_handlers=[
        AuthController,
        UsuarioController,
        CompradorController,
        ConductorController,
        VehiculoController,
        TrailerController,
        DestinoController,
        OrigenController,
        PatioController,
        EntidadController,
        MedidaController,
        ProductoController,
        TransportadoraController,
        FacturaController,
        RegistroController,
        HistorialController,
    ],
    cors_config=cors_config,
    on_startup=[on_startup],
    openapi_config=OpenAPIConfig(title="API Sistema Ocean", version="3.0.0"),
)