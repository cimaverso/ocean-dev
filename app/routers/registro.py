# routers/registro.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from app.models.registro.modelo_registro import RegistroResponse, RegistroCreate, RegistroUpdate
from app.services.servicio_registro import RegistroService
from app.config.database import get_db
from app.core.core_auth import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
from datetime import date
from io import BytesIO
import traceback

router = APIRouter(
    prefix='/registro',
    tags=['Registro'],
    
)

@router.get("/exportar/ingresos", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_ingresos(consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    registro_service = RegistroService(db)
    output = registro_service.exportar_ingreso(consulta, fecha_inicio, fecha_fin)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar.")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=ingresos.xlsx"})

@router.get("/exportar/despachos", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_despachos(consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    registro_service = RegistroService(db)
    output = registro_service.exportar_despacho(consulta, fecha_inicio, fecha_fin)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar.")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=despachos.xlsx"})

@router.get("/exportar/servicios", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_servicios(consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    registro_service = RegistroService(db)
    output = registro_service.exportar_servicio(consulta, fecha_inicio, fecha_fin)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar.")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=servicios.xlsx"})

@router.get("/imprimir/{id}", response_class=StreamingResponse,status_code=status.HTTP_200_OK)
def imprimir_registro(id: int, db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    try:
        usuario_nombre = usuario.get("usuario_nombre")
        registro_servicio = RegistroService(db)
        pdf = registro_servicio.imprimir_registro(id, usuario_nombre)

        if not pdf:
            raise HTTPException(status_code=404, detail="Registro no encontrado")

        return StreamingResponse(BytesIO(pdf), media_type="application/pdf", headers={
            "Content-Disposition": f"inline; filename=registro_{id}.pdf"
        })

    except Exception as e:
        # Esto mostrará el motivo exacto del fallo
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )
    
    

@router.get("/estadistica/ingresos", include_in_schema=False, status_code=status.HTTP_200_OK)
def obtener_registro_peso(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    registro_servicie = RegistroService(db)
    registros = registro_servicie.calcular_ingresos()
    return registros

@router.get("/estadistica/despachos", include_in_schema=False, status_code=status.HTTP_200_OK)
def obtener_registro_peso(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    registro_servicie = RegistroService(db)
    registros = registro_servicie.calcular_despachos()
    return registros

# Listar registros finalizados
@router.get('/finalizado/{tipo}', response_model=list[RegistroResponse], status_code=status.HTTP_200_OK)
def obtener_registros_finalizados(tipo: int, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None, db: Session = Depends(get_db),  usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    registro_service = RegistroService(db)
    registros = registro_service.obtener_registros_finalizados(tipo, fecha_inicio, fecha_fin)

    return registros

#Listar registros en transito
@router.get('/transito', response_model=list[RegistroResponse], status_code=status.HTTP_200_OK)
def obtener_registros_transito(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    # Llamamos al servicio para obtener los registros
    registro_service = RegistroService(db)
    registros = registro_service.obtener_registros_transito()

    return registros

# Listar registros diarios
@router.get('/historial', response_model=list[RegistroResponse], status_code=status.HTTP_200_OK)
def obtener_registros_diarios(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    registro_service = RegistroService(db)
    registros = registro_service.obtener_registros_historial()

    return registros

# Obtener proximo id
@router.get('/consecutivo', include_in_schema=False, status_code=status.HTTP_200_OK)
def obtener_proximo_id(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    registro_service = RegistroService(db)
    proximo_id = registro_service.obtener_consecutivo()
    if not proximo_id:
        raise HTTPException(status_code=404, detail="No se pudo obtener el consecutivo")

    return {"proximo_id": proximo_id}

# Obtener proximo de tiquete
@router.get('/tiquete', include_in_schema=False, status_code=status.HTTP_200_OK)
def obtener_proximo_id_tiquete(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    registro_service = RegistroService(db)
    proximo_id_tiquete = registro_service.obtener_consecutivo_tiquete()
    if not proximo_id_tiquete:
        raise HTTPException(status_code=404, detail="No se pudo obtener el consecutivo de tiquete")

    return {"proximo_id_tiquete": proximo_id_tiquete}

# Crear Registro
@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_registro(registro: RegistroCreate, db: Session = Depends(get_db),  usuario: dict = Depends(obtener_usuario)):
    #Obtener el id del usuario 
    usuario_id = usuario.get("usuario_id")
    
    registro_service = RegistroService(db)
    nuevo_registro = registro_service.crear_registro(registro, usuario_id)

    if not nuevo_registro:
        raise HTTPException(status_code=400, detail="Error al crear el registro ")
    
    return {"mensaje": "Registro creado exitosamente."}
    
# Actualizar Registro
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_registro(id: int, registro: RegistroUpdate, db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    usuario_id = usuario.get("usuario_id")
    
    registro_service = RegistroService(db)
    registro_actualizado = registro_service.actualizar_registro(id, registro, usuario_id)

    if not registro_actualizado:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    return {"mensaje": "Registro actualizado exitosamente."}

#Abrir registr
@router.put("/abrir/{id}")
def abrir_registro(id: int, db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    service_registro = RegistroService(db)
    registro = service_registro.abrir_registro(id)

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
 
    return {"mensaje": "Registro abierto exitosamente."}

#Cerrar registro
@router.put("/cerrar/{id}")
def cerrar_registro(id: int, db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    service_registro = RegistroService(db)
    registro = service_registro.cerrar_registro(id)

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
 
    return {"mensaje": "Registro cerrado exitosamente."}