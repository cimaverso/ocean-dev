#test_comprador.py
#  Para ejecutar :pytest tests/test_comprador.py -v 

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

# Pruebas
def test_crear_comprador():
    """Prueba la creación de un comprador."""
    comprador_data = {
        "comp_nombre": "Test Comprador",
        "comp_nit": "123456789",
        "comp_telefono": "123456789",
        "comp_codigo": "TEST123"
    }
    response = client.post("/comprador/", json=comprador_data)
    assert response.status_code == 200
    assert response.json()["comp_nombre"] == "Test Comprador"

def test_listar_compradores():
    """Prueba la obtención de la lista de compradores."""
    response = client.get("/comprador/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_actualizar_comprador():
    """Prueba la actualización de un comprador."""
    comprador_data = {
        "comp_nombre": "Nuevo Nombre",
        "comp_nit": "987654321",
        "comp_telefono": "987654321",
        "comp_codigo": "NEWCODE"
    }
    # Crear un comprador primero
    response_post = client.post("/comprador/", json=comprador_data)
    assert response_post.status_code == 200
    comp_id = response_post.json()["comp_id"]

    # Actualizar comprador
    update_data = {"comp_nombre": "Nombre Actualizado"}
    response_put = client.put(f"/comprador/{comp_id}", json=update_data)
    assert response_put.status_code == 200
    assert response_put.json()["comp_nombre"] == "Nombre Actualizado"
