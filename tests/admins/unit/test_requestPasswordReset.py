import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from acesso_livre_api.src.admins import exceptions, service


@pytest.mark.asyncio
async def test_request_password_reset_success():
    """Testa sucesso no envio do email de reset de senha."""
    db_mock = AsyncMock()

    mock_admin = MagicMock()
    mock_admin.email = "validadmin@gmail.com"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_admin
    db_mock.execute = AsyncMock(return_value=mock_result)

    with patch(
        "acesso_livre_api.src.admins.service.send_password_reset_email",
        new_callable=AsyncMock,
    ) as mock_send_email:
        result = await service.request_password_reset(db_mock, "validadmin@gmail.com")

        assert result is not None
        assert result == {"message": "Enviamos um link de recuperação ao email."}
        db_mock.commit.assert_awaited_once()
        mock_send_email.assert_awaited_once()


@pytest.mark.asyncio
async def test_request_password_reset_admin_not_found():
    """Testa erro quando admin não existe."""
    db_mock = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db_mock.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(exceptions.AdminNotFoundException):
        await service.request_password_reset(db_mock, "validadmin@gmail.com")


@pytest.mark.asyncio
async def test_request_password_reset_email_send_failure():
    """Testa erro quando falha o envio do email."""
    db_mock = AsyncMock()

    mock_admin = MagicMock()
    mock_admin.email = "validadmin@gmail.com"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_admin
    db_mock.execute = AsyncMock(return_value=mock_result)

    with patch(
        "acesso_livre_api.src.admins.service.send_password_reset_email",
        new_callable=AsyncMock,
    ) as mock_send_email:
        mock_send_email.side_effect = Exception("SMTP connection error")

        with pytest.raises(exceptions.EmailSendException):
            await service.request_password_reset(db_mock, "validadmin@gmail.com")

        # Verificar que rollback foi chamado após erro de email
        assert db_mock.rollback.awaited


@pytest.mark.asyncio
async def test_request_password_reset_stores_token():
    """Verifica se o token de reset é armazenado no admin."""
    db_mock = AsyncMock()

    mock_admin = MagicMock()
    mock_admin.email = "validadmin@gmail.com"
    mock_admin.reset_token_hash = None
    mock_admin.reset_token_expires = None

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_admin
    db_mock.execute = AsyncMock(return_value=mock_result)

    with patch(
        "acesso_livre_api.src.admins.service.send_password_reset_email",
        new_callable=AsyncMock,
    ):
        await service.request_password_reset(db_mock, "validadmin@gmail.com")

        # Verificar que o token foi atribuído
        assert mock_admin.reset_token_hash is not None
        assert mock_admin.reset_token_expires is not None


@pytest.mark.asyncio
async def test_request_password_reset_email_called_with_correct_params():
    """Verifica se email é chamado com parâmetros corretos."""
    db_mock = AsyncMock()

    mock_admin = MagicMock()
    mock_admin.email = "validadmin@gmail.com"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_admin
    db_mock.execute = AsyncMock(return_value=mock_result)

    with patch(
        "acesso_livre_api.src.admins.service.send_password_reset_email",
        new_callable=AsyncMock,
    ) as mock_send_email:
        await service.request_password_reset(db_mock, "validadmin@gmail.com")

        # Verificar que foi chamado com o email correto
        mock_send_email.assert_awaited_once()
        call_kwargs = mock_send_email.call_args[1]
        assert call_kwargs["to_email"] == "validadmin@gmail.com"
        assert "code" in call_kwargs
        assert "reset_token" in call_kwargs


@pytest.mark.asyncio
async def test_request_password_reset_general_exception():
    """Testa tratamento de exceção genérica do banco."""
    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(side_effect=Exception("DB error"))

    with pytest.raises(exceptions.PasswordResetRequestException):
        await service.request_password_reset(db_mock, "validadmin@gmail.com")
