import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from acesso_livre_api.src.admins.email_service import send_password_reset_email


@pytest.mark.asyncio
class TestSendPasswordResetEmail:
    """Testa a função de envio de email de reset de senha via EmailJS."""

    @patch("acesso_livre_api.src.admins.email_service.httpx.AsyncClient")
    async def test_send_email_success(self, mock_client_class):
        """Testa envio bem-sucedido de email."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = await send_password_reset_email(
            to_email="admin@example.com", code="ABC123", reset_token="token123"
        )

        assert result is True
        mock_client.post.assert_called_once()

    @patch("acesso_livre_api.src.admins.email_service.httpx.AsyncClient")
    async def test_send_email_calls_emailjs_api(self, mock_client_class):
        """Verifica se a API do EmailJS é chamada corretamente."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        to_email = "admin@example.com"
        code = "ABC123"
        token = "token123"

        await send_password_reset_email(to_email=to_email, code=code, reset_token=token)

        call_args = mock_client.post.call_args
        assert "https://api.emailjs.com/api/v1.0/email/send" in call_args[0]

        json_payload = call_args[1]["json"]
        assert json_payload["template_params"]["to_email"] == to_email
        assert json_payload["template_params"]["code"] == code
        assert "reset_url" in json_payload["template_params"]

    @patch("acesso_livre_api.src.admins.email_service.httpx.AsyncClient")
    async def test_send_email_api_error(self, mock_client_class):
        """Testa tratamento de erro da API do EmailJS."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with pytest.raises(Exception) as exc_info:
            await send_password_reset_email(
                to_email="admin@example.com", code="ABC123", reset_token="token123"
            )

        assert "EmailJS error" in str(exc_info.value)

    @patch("acesso_livre_api.src.admins.email_service.httpx.AsyncClient")
    async def test_send_email_timeout(self, mock_client_class):
        """Testa tratamento de timeout."""
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with pytest.raises(httpx.TimeoutException):
            await send_password_reset_email(
                to_email="admin@example.com", code="ABC123", reset_token="token123"
            )

    @patch("acesso_livre_api.src.admins.email_service.httpx.AsyncClient")
    async def test_send_email_request_error(self, mock_client_class):
        """Testa tratamento de erro de requisição."""
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.RequestError("Connection error")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with pytest.raises(httpx.RequestError):
            await send_password_reset_email(
                to_email="admin@example.com", code="ABC123", reset_token="token123"
            )

    @patch("acesso_livre_api.src.admins.email_service.httpx.AsyncClient")
    async def test_send_email_generic_exception(self, mock_client_class):
        """Testa tratamento de exceção genérica."""
        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("Unexpected error")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with pytest.raises(Exception):
            await send_password_reset_email(
                to_email="admin@example.com", code="ABC123", reset_token="token123"
            )

    @patch("acesso_livre_api.src.admins.email_service.httpx.AsyncClient")
    async def test_send_email_to_correct_recipient(self, mock_client_class):
        """Verifica se o email é enviado para o destinatário correto."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        to_email = "specific@example.com"

        await send_password_reset_email(
            to_email=to_email, code="ABC123", reset_token="token123"
        )

        call_args = mock_client.post.call_args
        json_payload = call_args[1]["json"]
        assert json_payload["template_params"]["to_email"] == to_email

    @patch("acesso_livre_api.src.admins.email_service.httpx.AsyncClient")
    async def test_send_email_contains_reset_url(self, mock_client_class):
        """Verifica se o email contém a URL de reset correta."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        to_email = "admin@example.com"
        code = "ABC123DEF"
        token = "jwt.token"

        await send_password_reset_email(to_email=to_email, code=code, reset_token=token)

        call_args = mock_client.post.call_args
        json_payload = call_args[1]["json"]
        reset_url = json_payload["template_params"]["reset_url"]

        assert "password-reset" in reset_url
        assert to_email in reset_url
        assert code in reset_url
        assert token in reset_url
