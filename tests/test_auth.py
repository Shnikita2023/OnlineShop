from httpx import Response, AsyncClient

from tests.conftest import client


# async def test_register_client_async(async_client: AsyncClient):
#     response: Response = await async_client.post(url="/api/v1/register/", json={
#         "username": "stridngd!",
#         "password": "stringd",
#         "email": "user@example.com"
#     })
#     assert response.status_code == 201
#
def test_register_client():
    response: Response = client.post(url="/api/v1/register/", json={
        "username": "string",
        "password": "string",
        "email": "user@example.com"
    })
    assert response.status_code == 201
    print(response.json())



