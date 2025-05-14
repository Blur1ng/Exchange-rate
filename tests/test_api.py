import pytest
from httpx import AsyncClient, ASGITransport
from app.api.endpoints.users import router_users


"""
------------------START TESTS------------------
docker exec -it exchange-rate-fastapi-1 pytest
"""

@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(
        transport=ASGITransport(router_users),
        base_url="http://test"
        ) as ac:
        login_data = {"id": None, "username": "admin", "password": "vjnjh421"}
        response = await ac.post("/api/v1/auth/login/", json=login_data)

    assert response.status_code == 200
    