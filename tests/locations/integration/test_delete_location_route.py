
from unittest.mock import patch
from fastapi.testclient import TestClient
from acesso_livre_api.src.main import app
from acesso_livre_api.src.admins import dependencies

client = TestClient(app)

# Override dependencies to bypass auth

import pytest

@pytest.fixture
def override_auth():
    app.dependency_overrides[dependencies.simple_token_verification] = lambda: True
    yield
    app.dependency_overrides.pop(dependencies.simple_token_verification, None)

def test_delete_location_returns_correct_response(override_auth):
    """Test that delete location returns the correct JSON response structure."""
    with patch("acesso_livre_api.src.locations.service.delete_location") as mock_delete:
        mock_delete.return_value = True
        
        # We use strict=False for the patch to work with async functions if needed, 
        # but here we are mocking the service call completely.
        
        response = client.delete("/api/locations/1")
        
        assert response.status_code == 200
        assert response.json() == {"message": "Localização deletada com sucesso"}
