from pydantic import BaseModel

class ProcesoProductoResponse(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}