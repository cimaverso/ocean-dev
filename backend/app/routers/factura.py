from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.factura import FacturaResponse, FacturaCreate, FacturaUpdate
from app.services.factura import FacturaService
from app.config.database import get_db
from app.core.security import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/factura',
    tags=['Factura']
)

@router.get("/exportar", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_facturas(consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    output = FacturaService(db).exportar_facturas(consulta)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail="No hay datos para exportar")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=facturas.xlsx"})

@router.get('/', response_model=list[FacturaResponse], status_code=status.HTTP_200_OK)
def obtener_facturas(db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return FacturaService(db).listar_facturas()

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_factura(factura: FacturaCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    nuevo = FacturaService(db).crear_factura(factura)
    if not nuevo:
        raise HTTPException(status_code=400, detail="Error al crear la factura")
    return {"message": "Factura creada exitosamente."}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_factura(id: int, factura: FacturaUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    actualizada = FacturaService(db).actualizar_factura(id, factura)
    if not actualizada:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return {"message": "Factura actualizada exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_factura(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    if not FacturaService(db).eliminar_factura(id):
        raise HTTPException(status_code=404, detail="Factura no encontrada")