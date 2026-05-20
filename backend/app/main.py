from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (comprador, destino, origen, patio, entidad, producto,
                     conductor, vehiculo, trailer, usuario, registro, transportadora,
                     factura, medida, proceso, autenticacion, historial)


from app.config.database import engine  # Importar el engine donde está configurada la base de datos
from sqlmodel import SQLModel
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select
from app.models.historial.modelo_historial import Historial
from datetime import datetime, timedelta


#Instancias 
app = FastAPI(
    title="API Sistema Ocean SYT",
    version="1.0.0",
       
)


scheduler = BackgroundScheduler()

#SQLModel.metadata.create_all(engine)

# Configuracion de funcion para la eliminacion de datos en la tabla historial
def eliminar_registros_viejos():
    
    with Session(engine) as session:
        limite = datetime.utcnow() - timedelta(days=7)
        historial = session.exec(select(Historial).where(Historial.his_fecha < limite)).all()
        for h in historial:
            session.delete(h)
        session.commit()
        print(f"✅ Se eliminaron {len(historial)} registros.")

@app.on_event("startup")
def startup():
    # Configuración del job para que se ejecute el 30 de cada mes a las 00:00
    scheduler.add_job(
        eliminar_registros_viejos,
        trigger='cron',
        day=30,  
        hour=0,  
        minute=0  
    )
    scheduler.start()


# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"], 
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
    expose_headers=["Content-Disposition"] #Exponer encabezados específicos
)

# Rutas
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
#app.include_router(bascula.router)
app.include_router(usuario.router)
app.include_router(autenticacion.router)


