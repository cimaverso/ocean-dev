from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsuarioService:
    def __init__(self, db: Session):
        self.db = db

    def listar_usuarios(self):
        return self.db.execute(
            select(Usuario).options(selectinload(Usuario.rol))
        ).scalars().all()

    def crear_usuario(self, usuario_data: UsuarioCreate):
        data = usuario_data.model_dump()
        data["clave"] = bcrypt_context.hash(data["clave"])
        nuevo_usuario = Usuario(**data)
        self.db.add(nuevo_usuario)
        self.db.commit()
        self.db.refresh(nuevo_usuario)

        return self.db.execute(
            select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.id == nuevo_usuario.id)
        ).scalar_one_or_none()

    def actualizar_usuario(self, id: int, usuario_data: UsuarioUpdate):
        usuario_db = self.db.execute(
            select(Usuario).where(Usuario.id == id)
        ).scalar_one_or_none()

        if not usuario_db:
            return None

        update_data = usuario_data.model_dump(exclude_unset=True)

        if "clave" in update_data and update_data["clave"]:
            update_data["clave"] = bcrypt_context.hash(update_data["clave"])

        for key, value in update_data.items():
            setattr(usuario_db, key, value)

        self.db.commit()
        self.db.refresh(usuario_db)
        return usuario_db

   