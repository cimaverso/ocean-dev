from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.models.usuario.modelo_usuario import Usuario, UsuarioCreate, UsuarioUpdate
from passlib.context import CryptContext
from typing import List

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UsuarioService:
    def __init__(self, db: Session):
        self.db = db

    def listar_usuarios(self) -> list[Usuario]:
        statement = select(Usuario).options(selectinload(Usuario.rol))
        results = self.db.exec(statement)
        return results.all()

    def crear_usuario(self, usuario_data: UsuarioCreate) -> Usuario:
        hashed_password = bcrypt_context.hash(usuario_data.usuario_clave)
        data = usuario_data.dict()
        data["usuario_clave"] = hashed_password

        nuevo_usuario = Usuario(**data)
        self.db.add(nuevo_usuario)
        self.db.commit()
        self.db.refresh(nuevo_usuario)

        statement = select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.usuario_id == nuevo_usuario.usuario_id)
        return self.db.exec(statement).first()

    def actualizar_usuario(self, usuario_id: int, usuario_data: UsuarioUpdate) -> Usuario:
        statement = select(Usuario).where(Usuario.usuario_id == usuario_id)
        usuario_db = self.db.exec(statement).first()
        if not usuario_db:
            return None

        update_data = usuario_data.dict(exclude_unset=True)

        # Verifica si se proporcionó una nueva contraseña antes de hacer el hash
        if "usuario_clave" in update_data and update_data["usuario_clave"]:
            hashed_password = bcrypt_context.hash(update_data["usuario_clave"])
            update_data["usuario_clave"] = hashed_password  # Actualiza la contraseña con el hash

        # Actualiza los datos del usuario con los datos proporcionados
        for key, value in update_data.items():
            setattr(usuario_db, key, value)

        self.db.commit()
        self.db.refresh(usuario_db)
        return usuario_db

    def eliminar_usuario(self, usuario_id: int) -> bool:
        statement = select(Usuario).where(Usuario.usuario_id == usuario_id)
        usuario_db = self.db.exec(statement).first()

        if not usuario_db:
            return False

        self.db.delete(usuario_db)
        self.db.commit()
        return True

