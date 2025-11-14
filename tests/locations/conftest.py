import pytest_asyncio
from httpx import AsyncClient

from acesso_livre_api.src.locations.models import AccessibilityItem


@pytest_asyncio.fixture(scope="function")
def created_accessibility_item(db_session):
    """Cria um item de acessibilidade para testes."""
    item = AccessibilityItem(name="Item Teste", icon_url="icon.svg")
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest_asyncio.fixture(scope="function")
async def created_location(client: AsyncClient, created_accessibility_item, admin_auth_header):
    """Cria um local com itens de acessibilidade para testes."""
    location_data = {
        "name": "Local de Teste",
        "description": "Descricao do local",
        "top": 10.0,
        "left": 20.0
    }
    response = await client.post("/api/locations/", json=location_data, headers=admin_auth_header)
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.text}")
    return response.json()