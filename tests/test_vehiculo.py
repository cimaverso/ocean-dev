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
# ====== PRUEBAS PARA VEHICULO ======
def test_crear_vehiculo():
    """Prueba la creación de un vehículo."""
    vehiculo_data = {"vehi_placa": "ABC123"}
    response = client.post("/vehiculo/", json=vehiculo_data)
    assert response.status_code == 200
    assert response.json()["vehi_placa"] == "ABC123"

def test_listar_vehiculos():
    """Prueba la obtención de la lista de vehiculos."""
    response = client.get("/vehiculo/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_actualizar_vehiculo():
    """Prueba la actualización de un vehículo."""
    vehiculo_data = {"vehi_placa": "XYZ789"}
    response = client.put("/vehiculo/1", json=vehiculo_data)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert response.json()["vehi_placa"] == "XYZ789"