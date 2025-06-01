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
# ====== PRUEBAS PARA TRAILER ======
def test_crear_trailer():
    """Prueba la creación de un trailer."""
    trailer_data = {"trai_trailer": "Trailer Test"}
    response = client.post("/trailer/", json=trailer_data)
    assert response.status_code == 200
    assert response.json()["trai_trailer"] == "Trailer Test"

def test_listar_trailers():
    """Prueba la obtención de la lista de trailers."""
    response = client.get("/trailer/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)    

def test_actualizar_trailer():
    """Prueba la actualización de un trailer."""
    trailer_data = {"trai_trailer": "Trailer Modificado"}
    response = client.put("/trailer/1", json=trailer_data)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert response.json()["trai_trailer"] == "Trailer Modificado"



