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

# ====== PRUEBAS PARA PRODUCTO ======
def test_crear_producto():
    """Prueba la creación de un producto."""
    producto_data = {
        "prod_nombre": "Producto Test",
        "prod_idunidadmedida": 1,
        "prod_idtipoproducto": 1,
        "prod_codigo": "PROD123",
        "prod_idprocesoprod": 2
    }
    response = client.post("/producto/producto", json=producto_data)
    assert response.status_code == 201
    assert response.json()["prod_nombre"] == "Producto Test"

def test_listar_productos():
    """Prueba la obtención de la lista de productos."""
    response = client.get("/producto/")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert isinstance(response.json(), list)

def test_listar_servicios():
    """Prueba la obtención de la lista de servicios."""
    response = client.get("/producto/productos/servicios")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert isinstance(response.json(), list)
def test_actualizar_producto():
    """Prueba la actualización de un producto."""
    producto_data = {"prod_nombre": "Producto Modificado"}
    response = client.put("/producto/producto/1", json=producto_data)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert response.json()["prod_nombre"] == "Producto Modificado"