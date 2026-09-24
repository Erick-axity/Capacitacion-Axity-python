from fastapi.testclient import TestClient

# Importamos tu app de FastAPI desde la subcarpeta
from modulo_ci_cd_y_docker.main import app

# Creamos el cliente de pruebas en memoria
client = TestClient(app)


def test_flujo_completo_api():
    # Ya no necesitamos aiohttp ni async/await. Todo es instantáneo en memoria.

    # 1. TEST DE LOGIN Y JWT
    datos_login = {"username": "admin", "password": "123"}
    # Las peticiones ahora se hacen usando 'client'
    response_login = client.post("/api/v1/login", data=datos_login)

    assert response_login.status_code == 200
    data = response_login.json()
    token = data["access_token"]
    assert token is not None

    # Preparamos las llaves de seguridad
    headers = {"Authorization": f"Bearer {token}"}

    # 2. TEST DEL CRUD (Crear Order)
    nueva_orden = {"producto": "Laptop Pro", "cantidad": 1, "precio": 1500.0}
    response_orden = client.post("/api/v1/orders/", json=nueva_orden, headers=headers)

    assert response_orden.status_code == 200
    orden_creada = response_orden.json()
    assert orden_creada["producto"] == "Laptop Pro"

    # Validamos que devuelva un ID dinámico como aprendimos
    assert isinstance(orden_creada["id"], int)
    assert orden_creada["id"] > 0
