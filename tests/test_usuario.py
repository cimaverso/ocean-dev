import pytest
from fastapi.testclient import TestClient
from backend.main import app
from config.database import get_db, Base, engine, SessionLocal
from sqlalchemy.orm import Session

# Cliente de pruebas
client = TestClient(app)

# Configuración de base de datos para pruebas
@pytest.fixture(scope="function")
def db_session():
    """Crea una base de datos en memoria para pruebas y la limpia después."""
    Base.metadata.create_all(bind=engine)   # Crea las tablas en la BD de prueba
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Elimina tablas después de la prueba

# Mock de dependencia para usar base de datos de pruebas
def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
# ====== PRUEBAS PARA USUARIO ======
def test_crear_usuario():
    """Prueba la creación de un usuario."""
    usuario_data = {
        "user_name": "usuario_test",
        "user_password": "password123",
        "user_email": "usuario@test.com",
        "user_idrol": 1,
        "user_estado": "activo"
    }
    response = client.post("/usuario/", json=usuario_data)
    assert response.status_code == 201
    assert response.json()["user_name"] == "usuario_test"

def test_listar_usuario():
    """Prueba la obtención de la lista de usuarios."""
    response = client.get("/usuario/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_actualizar_usuario():
    """Prueba la actualización de un usuario."""
    usuario_data = {"user_name": "usuario_modificado"}
    response = client.put("/usuario/1", json=usuario_data)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert response.json()["user_name"] == "usuario_modificado"
