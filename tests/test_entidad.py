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


def test_crear_entidad():
    """Prueba la creación de una entidad (proveedor, cliente o tercero)."""
    entidad_data = {
        "ent_idtipoentidad": 1,  # Proveedor
        "ent_nombre": "Proveedor XYZ",
        "ent_nit": "900123456",
        "ent_codigo": "PRV001",
        "ent_ciudad": "Cali",
        "ent_telefono": "3123456789"
    }
    response = client.post("/entidad/entidad", json=entidad_data)
    assert response.status_code == 201
    assert response.json()["ent_nombre"] == "Proveedor XYZ"

def test_listar_proveedores():
    """Prueba la obtención de proveedores."""
    response = client.get("/entidad/proveedores")
    assert response.status_code in [200, 404]  
    if response.status_code == 200:
        assert isinstance(response.json(), list)

def test_listar_clientes():
    """Prueba la obtención de clientes."""
    response = client.get("/entidad/clientes")
    assert response.status_code in [200, 404]  
    if response.status_code == 200:
        assert isinstance(response.json(), list)

def test_listar_terceros():
    """Prueba la obtención de terceros."""
    response = client.get("/entidad/terceros")
    assert response.status_code in [200, 404]  
    if response.status_code == 200:
        assert isinstance(response.json(), list)

def test_actualizar_entidad():
    """Prueba la actualización de una entidad."""
    entidad_data = {
        "ent_idtipoentidad": 2,  # Cliente
        "ent_nombre": "Cliente ABC",
        "ent_nit": "800654321",
        "ent_codigo": "CLI002",
        "ent_ciudad": "Bogotá",
        "ent_telefono": "3109876543"
    }
    # Crear una entidad primero
    response_post = client.post("/entidad/entidad", json=entidad_data)
    assert response_post.status_code == 201
    ent_id = response_post.json()["ent_id"]

    # Datos a actualizar
    update_data = {"ent_nombre": "Cliente Modificado"}
    response_put = client.put(f"/entidad/entidad/{ent_id}", json=update_data)
    assert response_put.status_code == 200
    assert response_put.json()["ent_nombre"] == "Cliente Modificado"
