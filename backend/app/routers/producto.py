from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.producto import ProductoResponse, ProductoCreate, ProductoUpdate
from app.services.producto import ProductoService
from app.config.database import get_db
from app.core.security import obtener_usuario, verificar_rol
from fastapi.responses import StreamingResponse
from typing import Optional

router = APIRouter(
    prefix='/producto',
    tags=['Productos']
)

@router.get("/exportar/{tipo}", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_producto(tipo: int, consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    output = ProductoService(db).exportar_productos(tipo, consulta)
    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar de tipo {tipo}.")
    filename = {1: "productos.xlsx", 2: "servicios.xlsx"}.get(tipo, "producto.xlsx")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename={filename}"})

@router.get('/{tipo}', response_model=list[ProductoResponse], status_code=status.HTTP_200_OK)
def obtener_producto_tipo(tipo: int, db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    return ProductoService(db).listar_productos_tipo(tipo)

@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    nuevo = ProductoService(db).crear_producto(producto)
    if not nuevo:
        raise HTTPException(status_code=400, detail="Error al crear el producto")
    return {"message": "Producto creado exitosamente."}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_producto(id: int, producto: ProductoUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    actualizado = ProductoService(db).actualizar_producto(id, producto)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": "Producto actualizado exitosamente."}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    if not ProductoService(db).eliminar_producto(id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")