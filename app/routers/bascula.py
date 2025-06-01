from fastapi import APIRouter
from app.services.servicio_bascula import leer_peso

router = APIRouter(
    prefix='/bascula',
    tags=['Bascula']
)

@router.get("/peso")
async def obtener_peso():
    return {"peso": leer_peso()}
