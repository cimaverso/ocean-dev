from pydantic import BaseModel

class TipoEntidadResponse(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}