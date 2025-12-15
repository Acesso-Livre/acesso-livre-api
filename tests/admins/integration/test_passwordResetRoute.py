import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

user_data = {
    "email": "reset.user@empresa.com",
    "password": "OldPassword123!",
    "new_password": "NewPassword456!",
}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_forgot_password_success(client: AsyncClient, admin_auth_header):
    """Testa a solicitação de recuperação de senha com um email válido."""
    user_to_register = {"email": "reset.user@empresa.com", "password": "OldPassword123!"}
    await client.post("/api/admins/register", json=user_to_register, headers=admin_auth_header)

    with patch(
        "acesso_livre_api.src.admins.service.send_password_reset_email",
        new_callable=AsyncMock,
    ):
        res = await client.post(
            "/api/admins/forgot-password", json={"email": user_data["email"]}
        )

    assert res.status_code == 200
    assert res.json() == {"message": "Enviamos um link de recuperação ao email."}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_forgot_password_nonexistent_email(client: AsyncClient):
    """Testa a solicitação de recuperação de senha com um email inexistente."""
    with patch(
        "acesso_livre_api.src.admins.service.send_password_reset_email",
        new_callable=AsyncMock,
    ):
        res = await client.post(
            "/api/admins/forgot-password", json={"email": "not.found@empresa.com"}
        )

    assert res.status_code == 404
    assert res.json()["detail"] == "Administrador não encontrado"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_password_reset_success(client: AsyncClient, monkeypatch, admin_auth_header):
    """Testa a atualização da senha com um token/código válido."""
    user_to_register = {"email": "reset.user@empresa.com", "password": "OldPassword123!"}
    await client.post("/api/admins/register", json=user_to_register, headers=admin_auth_header)

    fixed_code = "123456"
    monkeypatch.setattr(
        "acesso_livre_api.src.admins.utils.gen_code_for_reset_password",
        lambda: fixed_code,
    )

    with patch(
        "acesso_livre_api.src.admins.service.send_password_reset_email",
        new_callable=AsyncMock,
    ):
        await client.post(
            "/api/admins/forgot-password", json={"email": user_data["email"]}
        )

    reset_payload = {
        "token": fixed_code,
        "email": user_data["email"],
        "new_password": user_data["new_password"],
    }
    res = await client.post("/api/admins/password-reset", json=reset_payload)

    assert res.status_code == 200
    assert res.json() == {"message": "Senha atualizada com sucesso!"}

    login_payload = {"email": user_data["email"], "password": user_data["new_password"]}
    login_res = await client.post("/api/admins/login", json=login_payload)
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_password_reset_invalid_token(client: AsyncClient, admin_auth_header):
    """Testa a atualização da senha com um token/código inválido."""

    user_to_register = {"email": "reset.user@empresa.com", "password": "OldPassword123!"}
    await client.post("/api/admins/register", json=user_to_register, headers=admin_auth_header)

    with patch(
        "acesso_livre_api.src.admins.service.send_password_reset_email",
        new_callable=AsyncMock,
    ):
        await client.post(
            "/api/admins/forgot-password", json={"email": user_data["email"]}
        )

    reset_payload = {
        "token": "invalidcode",
        "email": user_data["email"],
        "new_password": "SomeNewPassword123!",
    }
    res = await client.post("/api/admins/password-reset", json=reset_payload)

    assert res.status_code == 400
    assert res.json()["detail"] == "Código inválido"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_forgot_password_email_failure(client: AsyncClient, admin_auth_header):
    """Testa erro quando falha o envio de email."""
    user_to_register = {"email": "reset.user@empresa.com", "password": "OldPassword123!"}
    await client.post("/api/admins/register", json=user_to_register, headers=admin_auth_header)

    with patch(
        "acesso_livre_api.src.admins.service.send_password_reset_email",
        new_callable=AsyncMock,
    ) as mock_send:
        mock_send.side_effect = Exception("SMTP connection error")
        res = await client.post(
            "/api/admins/forgot-password", json={"email": user_data["email"]}
        )

    assert res.status_code == 500
