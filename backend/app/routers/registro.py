from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.registro import RegistroResponse, RegistroCreate, RegistroUpdate
from app.services.registro import RegistroService
from app.config.database import get_db
from app.core.security import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import date

router = APIRouter(
    prefix='/registro',
    tags=['Registro']
)

@router.get("/exportar/ingresos", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_ingresos(consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    output = RegistroService(db).exportar_ingreso(consulta, fecha_inicio, fecha_fin)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail="No hay datos para exportar.")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=ingresos.xlsx"})

@router.get("/exportar/despachos", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_despachos(consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    output = RegistroService(db).exportar_despacho(consulta, fecha_inicio, fecha_fin)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail="No hay datos para exportar.")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=despachos.xlsx"})

@router.get("/exportar/servicios", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_servicios(consulta: Optional[str] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    output = RegistroService(db).exportar_servicio(consulta, fecha_inicio, fecha_fin)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail="No hay datos para exportar.")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=servicios.xlsx"})

@router.get("/estadistica/ingresos", status_code=status.HTTP_200_OK)
def obtener_estadistica_ingresos(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return RegistroService(db).calcular_ingresos()

@router.get("/estadistica/despachos", status_code=status.HTTP_200_OK)
def obtener_estadistica_despachos(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return RegistroService(db).calcular_despachos()

@router.get('/finalizado/{tipo}', response_model=list[RegistroResponse], status_code=status.HTTP_200_OK)
def obtener_registros_finalizados(tipo: int, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    return RegistroService(db).obtener_registros_finalizados(tipo, fecha_inicio, fecha_fin)

@router.get('/transito', response_model=list[RegistroResponse], status_code=status.HTTP_200_OK)
def obtener_registros_transito(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return RegistroService(db).obtener_registros_transito()

@router.get('/historial', response_model=list[RegistroResponse], status_code=status.HTTP_200_OK)
def obtener_registros_diarios(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return RegistroService(db).obtener_registros_historial()

@router.get('/consecutivo', include_in_schema=False, status_code=status.HTTP_200_OK)
def obtener_proximo_id(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    proximo_id = RegistroService(db).obtener_consecutivo()
    if not proximo_id:
        raise HTTPException(status_code=404, detail="No se pudo obtener el consecutivo")
    return {"proximo_id": proximo_id}

@router.get('/tiquete', include_in_schema=False, status_code=status.HTTP_200_OK)
def obtener_proximo_id_tiquete(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    proximo_id_tiquete = RegistroService(db).obtener_consecutivo_tiquete()
    if not proximo_id_tiquete:
        raise HTTPException(status_code=404, detail="No se pudo obtener el consecutivo de tiquete")
    return {"proximo_id_tiquete": proximo_id_tiquete}

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_registro(registro: RegistroCreate, db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    usuario_id = usuario.get("usuario_id")
    nuevo = RegistroService(db).crear_registro(registro, usuario_id)
    if not nuevo:
        raise HTTPException(status_code=400, detail="Error al crear el registro")
    return {"mensaje": "Registro creado exitosamente."}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_registro(id: int, registro: RegistroUpdate, db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    usuario_id = usuario.get("usuario_id")
    actualizado = RegistroService(db).actualizar_registro(id, registro, usuario_id)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return {"mensaje": "Registro actualizado exitosamente."}