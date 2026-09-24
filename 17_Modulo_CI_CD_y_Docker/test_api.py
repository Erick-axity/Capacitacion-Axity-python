import aiohttp
import pytest


# Le decimos a pytest que esta es una prueba asíncrona
@pytest.mark.asyncio
async def test_flujo_completo_api():
    base_url = "http://127.0.0.1:8000/api/v1"

    # aiohttp ClientSession es el navegador virtual que hace las peticiones
    async with aiohttp.ClientSession() as session:

        # 1. TEST DE LOGIN Y JWT
        datos_login = {"username": "admin", "password": "123"}
        async with session.post(f"{base_url}/login", data=datos_login) as response:
            assert response.status == 200
            data = await response.json()
            token = data["access_token"]
            assert token is not None

        # Preparamos las llaves de seguridad para las siguientes peticiones
        headers = {"Authorization": f"Bearer {token}"}

        # 2. TEST DEL CRUD (Crear Order)
        nueva_orden = {"producto": "Laptop Pro", "cantidad": 1, "precio": 1500.0}
        async with session.post(
            f"{base_url}/orders/", json=nueva_orden, headers=headers
        ) as response:
            assert response.status == 200
            orden_creada = await response.json()
            assert orden_creada["producto"] == "Laptop Pro"
            assert isinstance(orden_creada["id"], int)
            assert orden_creada["id"] > 0
