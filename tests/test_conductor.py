#  Para ejecutar :pytest tests/test_conductor.py -v 

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
    Base.metadata.create_all(bind=engine)  # Crea las tablas en la BD de pruebas
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Elimina las tablas al finalizar

# Mock de dependencia para usar base de datos de pruebas
def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Prueba: Crear un conductor
def test_crear_conductor():
    """Prueba la creación de un conductor."""
    conductor_data = {
        "conduct_nombre": "Juan Pérez",
        "conduct_cedula": "123456789",
        "conduct_telefono": "3112345678"
    }
    response = client.post("/conductor/", json=conductor_data)
    assert response.status_code == 200
    assert response.json()["conduct_nombre"] == "Juan Pérez"

# Prueba: Listar conductores
def test_listar_conductores():
    """Prueba la obtención de la lista de conductores."""
    response = client.get("/conductor/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Prueba: Actualizar un conductor
def test_actualizar_conductor():
    """Prueba la actualización de un conductor."""
    conductor_data = {
        "conduct_nombre": "Pedro López",
        "conduct_cedula": "987654321",
        "conduct_telefono": "3223456789"
    }
    # Crear un conductor primero
    response_post = client.post("/conductor/", json=conductor_data)
    assert response_post.status_code == 200
    conduct_id = response_post.json()["conduct_id"]

    # Datos a actualizar
    update_data = {"conduct_nombre": "Pedro Actualizado"}
    response_put = client.put(f"/conductor/{conduct_id}", json=update_data)
    assert response_put.status_code == 200
    assert response_put.json()["conduct_nombre"] == "Pedro Actualizado"
