from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from src.features.auth.models import Usuario
from src.features.auth.schemas import UsuarioCreate, UsuarioUpdate
from src.core.security import hash_password, verificar_password


def usuario_autenticado(usuario_nombre: str, usuario_clave: str, db: Session):
    usuario = db.execute(
        select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.nombre == usuario_nombre)
    ).scalar_one_or_none()
    if not usuario or not verificar_password(usuario_clave, usuario.clave):
        return None
    return usuario


class UsuarioService:
    def __init__(self, db: Session):
        self.db = db

    def listar_usuarios(self) -> list[Usuario]:
        return self.db.execute(
            select(Usuario).options(selectinload(Usuario.rol))
        ).scalars().all()

    def crear_usuario(self, data: UsuarioCreate) -> Usuario:
        payload = data.model_dump()
        payload["clave"] = hash_password(payload["clave"])
        nuevo = Usuario(**payload)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return self.db.execute(
            select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.id == nuevo.id)
        ).scalar_one_or_none()

    def actualizar_usuario(self, id: int, data: UsuarioUpdate) -> Usuario | None:
        usuario = self.db.execute(
            select(Usuario).where(Usuario.id == id)
        ).scalar_one_or_none()
        if not usuario:
            return None
        update_data = data.model_dump(exclude_unset=True)
        if "clave" in update_data and update_data["clave"]:
            update_data["clave"] = hash_password(update_data["clave"])
        for key, value in update_data.items():
            setattr(usuario, key, value)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario