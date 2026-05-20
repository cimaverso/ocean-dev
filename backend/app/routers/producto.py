from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.registro.producto.modelo_producto import ProductoResponse, ProductoCreate, ProductoUpdate
from app.services.servicio_producto import ProductoService
from app.config.database import get_db
from fastapi.responses import StreamingResponse
from typing import Optional
from app.core.core_auth import obtener_usuario, verificar_rol

router = APIRouter(
    prefix='/producto',
    tags=['Productos']
)

#Exportar productos por tipo
@router.get("/exportar/{tipo}", response_class=StreamingResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
def exportar_producto( tipo: int, consulta: Optional[str] = None, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    producto_service = ProductoService(db)
    output = producto_service.exportar_productos(tipo, consulta)

    if output.getbuffer().nbytes == 0:
        raise HTTPException(status_code=404, detail=f"No hay datos para exportar de tipo {tipo}.")

    filename = {1: "productos.xlsx", 2: "servicios.xlsx"}.get(tipo, "producto.xlsx")
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename={filename}"})

# Listar productos por tipo
@router.get('/{tipo}', response_model=list[ProductoResponse], status_code=status.HTTP_200_OK)
def obtener_producto_tipo(tipo: int, db: Session = Depends(get_db), usuario: dict = Depends(obtener_usuario)):
    producto_service = ProductoService(db)
    productos = producto_service.listar_productos_tipo(tipo)

    return productos

# Crear producto
@router.post('/', status_code=status.HTTP_201_CREATED)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    producto_service = ProductoService(db)
    nuevo_producto = producto_service.crear_producto(producto)
    if not nuevo_producto:
        raise HTTPException(status_code=400, detail="Error al crear el producto")
    
    return {"message": "Producto creado exitosamente."}

# Actualizar producto
@router.put("/{id}", status_code=status.HTTP_200_OK)
def actualizar_producto(id: int, producto: ProductoUpdate, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    producto_service = ProductoService(db)
    producto_actualizado = producto_service.actualizar_producto(id, producto)

    if not producto_actualizado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return {"message": "Producto actualizado exitosamente."}    

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(id: int, db: Session = Depends(get_db), usuario: dict = Depends(verificar_rol(['ADMINISTRADOR']))):
    producto_service = ProductoService(db)
    eliminado = producto_service.eliminar_producto(id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return {"message": "Producto eliminado exitosamente."} 
