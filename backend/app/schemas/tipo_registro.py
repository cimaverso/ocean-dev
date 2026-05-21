from pydantic import BaseModel

class TipoRegistroResponse(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}