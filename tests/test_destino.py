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

def test_crear_destino():
    """Prueba la creación de un destino."""
    destino_data = {
        "dest_nombre": "Bogotá",
        "dest_codigo": "BOG123"
    }
    response = client.post("/destino/", json=destino_data)
    assert response.status_code == 201
    assert response.json()["dest_nombre"] == "Bogotá"

def test_listar_destinos():
    """Prueba la obtención de la lista de destinos."""
    response = client.get("/destino/")
    assert response.status_code in [200, 404]  # Puede devolver 404 si la BD está vacía
    if response.status_code == 200:
        assert isinstance(response.json(), list)

def test_actualizar_destino():
    """Prueba la actualización de un destino."""
    destino_data = {
        "dest_nombre": "Medellín",
        "dest_codigo": "MED456"
    }
    # Crear un destino primero
    response_post = client.post("/destino/", json=destino_data)
    assert response_post.status_code == 201
    dest_id = response_post.json()["dest_id"]

    # Datos a actualizar
    update_data = {"dest_nombre": "Medellín Actualizado"}
    response_put = client.put(f"/destino/{dest_id}", json=update_data)
    assert response_put.status_code == 200
    assert response_put.json()["dest_nombre"] == "Medellín Actualizado"
