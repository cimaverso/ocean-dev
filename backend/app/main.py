from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (comprador, destino, origen, patio, entidad, producto,
                         conductor, vehiculo, trailer, usuario, registro, transportadora,
                         factura, medida, proceso, autenticacion, historial)
from app.config.database import engine
from app.models.historial import Historial
from sqlalchemy.orm import Session
from sqlalchemy import select
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

app = FastAPI(
    title="API Sistema Ocean",
    version="3.0.0",
)

scheduler = BackgroundScheduler()

def eliminar_registros_viejos():
    with Session(engine) as session:
        limite = datetime.utcnow() - timedelta(days=7)
        historial = session.execute(
            select(Historial).where(Historial.fecha < limite)
        ).scalars().all()
        for h in historial:
            session.delete(h)
        session.commit()
        print(f"✅ Se eliminaron {len(historial)} registros.")

@app.on_event("startup")
def startup():
    scheduler.add_job(
        eliminar_registros_viejos,
        trigger='cron',
        day=30,
        hour=0,
        minute=0
    )
    scheduler.start()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

app.include_router(autenticacion.router)
app.include_router(usuario.router)
app.include_router(comprador.router)
app.include_router(destino.router)
app.include_router(origen.router)
app.include_router(patio.router)
app.include_router(entidad.router)
app.include_router(producto.router)
app.include_router(medida.router)
app.include_router(proceso.router)
app.include_router(conductor.router)
app.include_router(vehiculo.router)
app.include_router(trailer.router)
app.include_router(registro.router)
app.include_router(transportadora.router)
app.include_router(factura.router)
app.include_router(historial.router)