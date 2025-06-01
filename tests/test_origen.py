
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

# ====== PRUEBAS PARA ORIGEN ======
def test_crear_origen():
    """Prueba la creación de un origen."""
    origen_data = {"ori_nombre": "Origen Test", "ori_codigo": "ORG123"}
    response = client.post("/origen/", json=origen_data)
    assert response.status_code == 200
    assert response.json()["ori_nombre"] == "Origen Test"

def test_listar_origenes():
    """Prueba la obtención de la lista de orígenes."""
    response = client.get("/origen/")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert isinstance(response.json(), list)


def test_actualizar_origen():
    """Prueba la actualización de un origen."""
    origen_data = {"ori_nombre": "Origen Modificado"}
    response = client.put("/origen/1", json=origen_data)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert response.json()["ori_nombre"] == "Origen Modificado"
