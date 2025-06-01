from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.registro.modelo_comprador import CompradorResponse, CompradorCreate, CompradorUpdate
from app.services.servicio_comprador import CompradorService
from app.config.database import get_db
from app.core.core_auth import verificar_rol, obtener_usuario
from fastapi.responses import StreamingResponse
from typing import Optional


router = APIRouter(
    prefix='/comprador',
    tags=['Comprador'], 
  
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_compradores(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    comprador_service = CompradorService(db)
    output = comprador_service.exportar_compradores(consulta)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=compradores.xlsx"})

# Listar compradores
@router.get('/', response_model=list[CompradorResponse], status_code=status.HTTP_200_OK)
def obtener_compradores(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    # Verificamos el rol del usuario autenticado
    comprador_service = CompradorService(db)
    compradores = comprador_service.listar_compradores()

    return compradores

# Crear comprador
@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_comprador(comprador: CompradorCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["admin"])) ):
    comprador_service = CompradorService(db)
    nuevo_comprador = comprador_service.crear_comprador(comprador)

    if not nuevo_comprador:
        raise HTTPException(status_code=400, detail="Error al crear el comprador")

    return {"message": "Comprador creado exitosamente."}

# Actualizar comprador
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_comprador(id: int, comprador: CompradorUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["admin"])) ):
    comprador_service = CompradorService(db)

    comprador_actualizado = comprador_service.actualizar_comprador(id, comprador)
    if not comprador_actualizado:
        raise HTTPException(status_code=404, detail="Comprador no encontrado")

    return {"message": "Comprador actualizado exitosamente."}

# Eliminar comprador
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_comprador(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(["admin"])) ):
    comprador_service = CompradorService(db)
    eliminado = comprador_service.eliminar_comprador(id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Comprador no encontrado")

    return  {'message': 'Comprador eliminado correctamente'}
