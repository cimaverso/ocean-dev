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

# ====== PRUEBAS PARA PATIO ======
def test_crear_patio():
    """Prueba la creación de un patio."""
    patio_data = {"pat_nombre": "Patio Central", "pat_codigo": "PAT456"}
    response = client.post("/patio/", json=patio_data)
    assert response.status_code == 200
    assert response.json()["pat_nombre"] == "Patio Central"

def test_listar_patios():
    """Prueba la obtención de la lista de patios."""
    response = client.get("/patio/")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert isinstance(response.json(), list)


def test_actualizar_patio():
    """Prueba la actualización de un patio."""
    patio_data = {"pat_nombre": "Patio Modificado"}
    response = client.put("/patio/1", json=patio_data)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert response.json()["pat_nombre"] == "Patio Modificado"