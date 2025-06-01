# routers/factura.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.registro.modelo_factura import FacturaResponse, FacturaCreate, FacturaUpdate
from app.services.servicio_factura import FacturaService
from app.config.database import get_db
from app.core.core_auth import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/factura',
    tags=['Factura']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_facturas(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    factura_service = FacturaService(db)
    output = factura_service.exportar_facturas(consulta)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=facturas.xlsx"})

# Listar facturas
@router.get('/', response_model=list[FacturaResponse], status_code=status.HTTP_200_OK)
def obtener_facturas(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    factura_service = FacturaService(db)
    facturas = factura_service.listar_facturas()
    return facturas

# Crear factura
@router.post('/',  status_code=status.HTTP_201_CREATED)
def crear_factura(factura: FacturaCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    factura_service = FacturaService(db)
    nuevo_factura = factura_service.crear_factura(factura)
    if not nuevo_factura:
        raise HTTPException(status_code=400, detail="Error al crear la factura")
    return

# Actualizar factura
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_factura(id: int, factura: FacturaUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    factura_service = FacturaService(db)
    factura_actualizado = factura_service.actualizar_factura(id, factura)

    if not factura_actualizado:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    return {"message": "Factura actualizada exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_factura(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    factura_service = FacturaService(db)
    eliminado = factura_service.eliminar_factura(id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Factura no encontrado")

    return {"message": "Factura eliminado exitosamente."}
