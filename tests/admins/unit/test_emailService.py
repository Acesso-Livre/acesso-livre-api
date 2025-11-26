import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from acesso_livre_api.src.admins.email_service import (
    send_password_reset_email,
    create_password_reset_email_body,
)


class TestCreatePasswordResetEmailBody:
    """Testa a geração do corpo do email de reset de senha."""

    def test_email_body_contains_code(self):
        """Verifica se o corpo do email contém o código de reset."""
        email = "admin@example.com"
        code = "ABC123DEF"
        token = "jwt.token.here"

        body = create_password_reset_email_body(email, code, token)

        assert code in body
        assert "Recuperação de Senha" in body
        assert "15 minutos" in body

    def test_email_body_contains_reset_url(self):
        """Verifica se o corpo do email contém a URL de reset."""
        email = "admin@example.com"
        code = "ABC123DEF"
        token = "jwt.token.here"

        body = create_password_reset_email_body(email, code, token)

        assert "password-reset" in body
        assert email in body
        assert code in body
        assert token in body

    def test_email_body_is_html(self):
        """Verifica se o corpo é HTML válido."""
        email = "admin@example.com"
        code = "ABC123DEF"
        token = "jwt.token.here"

        body = create_password_reset_email_body(email, code, token)

        assert "<!DOCTYPE html>" in body
        assert "<html>" in body
        assert "</html>" in body
        assert "text/html" not in body  # Não é necessário marcar aqui

    def test_email_body_contains_warning_section(self):
        """Verifica se o email contém seção de aviso."""
        email = "admin@example.com"
        code = "ABC123DEF"
        token = "jwt.token.here"

        body = create_password_reset_email_body(email, code, token)

        assert "Atenção" in body or "aviso" in body.lower()
        assert "expirado" in body.lower()


@pytest.mark.asyncio
class TestSendPasswordResetEmail:
    """Testa a função de envio de email de reset de senha."""

    @patch("acesso_livre_api.src.admins.email_service.aiosmtplib.SMTP")
    async def test_send_email_success(self, mock_smtp_class):
        """Testa envio bem-sucedido de email."""
        # Mock do SMTP
        mock_smtp = AsyncMock()
        mock_smtp_class.return_value.__aenter__.return_value = mock_smtp

        result = await send_password_reset_email(
            to_email="admin@example.com", code="ABC123", reset_token="token123"
        )

        assert result is True
        mock_smtp.login.assert_called_once()
        mock_smtp.sendmail.assert_called_once()

    @patch("acesso_livre_api.src.admins.email_service.aiosmtplib.SMTP")
    async def test_send_email_calls_login(self, mock_smtp_class):
        """Verifica se o método login é chamado com credenciais corretas."""
        mock_smtp = AsyncMock()
        mock_smtp_class.return_value.__aenter__.return_value = mock_smtp

        await send_password_reset_email(
            to_email="admin@example.com", code="ABC123", reset_token="token123"
        )

        # Verificar que login foi chamado
        assert mock_smtp.login.called

    @patch("acesso_livre_api.src.admins.email_service.aiosmtplib.SMTP")
    async def test_send_email_calls_sendmail(self, mock_smtp_class):
        """Verifica se o método sendmail é chamado."""
        mock_smtp = AsyncMock()
        mock_smtp_class.return_value.__aenter__.return_value = mock_smtp

        to_email = "admin@example.com"
        code = "ABC123"
        token = "token123"

        await send_password_reset_email(to_email=to_email, code=code, reset_token=token)

        # Verificar que sendmail foi chamado
        assert mock_smtp.sendmail.called
        call_args = mock_smtp.sendmail.call_args
        assert to_email in call_args[0]

    @patch("acesso_livre_api.src.admins.email_service.aiosmtplib.SMTP")
    async def test_send_email_smtp_exception(self, mock_smtp_class):
        """Testa tratamento de exceção SMTP."""
        import aiosmtplib

        mock_smtp = AsyncMock()
        mock_smtp.sendmail.side_effect = aiosmtplib.SMTPException("Connection error")
        mock_smtp_class.return_value.__aenter__.return_value = mock_smtp

        with pytest.raises(aiosmtplib.SMTPException):
            await send_password_reset_email(
                to_email="admin@example.com", code="ABC123", reset_token="token123"
            )

    @patch("acesso_livre_api.src.admins.email_service.aiosmtplib.SMTP")
    async def test_send_email_generic_exception(self, mock_smtp_class):
        """Testa tratamento de exceção genérica."""
        mock_smtp = AsyncMock()
        mock_smtp.sendmail.side_effect = Exception("Unexpected error")
        mock_smtp_class.return_value.__aenter__.return_value = mock_smtp

        with pytest.raises(Exception):
            await send_password_reset_email(
                to_email="admin@example.com", code="ABC123", reset_token="token123"
            )

    @patch("acesso_livre_api.src.admins.email_service.aiosmtplib.SMTP")
    async def test_send_email_message_format(self, mock_smtp_class):
        """Verifica o formato da mensagem de email."""
        mock_smtp = AsyncMock()
        mock_smtp_class.return_value.__aenter__.return_value = mock_smtp

        to_email = "admin@example.com"
        code = "ABC123DEF"
        token = "jwt.token"

        await send_password_reset_email(to_email=to_email, code=code, reset_token=token)

        # Verificar que sendmail foi chamado com os argumentos corretos
        assert mock_smtp.sendmail.called
        call_args = mock_smtp.sendmail.call_args

        # Argumentos: (from_email, to_email, message_str)
        from_email = call_args[0][0]
        to_recipient = call_args[0][1]
        message_str = call_args[0][2]

        # Verificar estrutura de email (sem verificar conteúdo específico que pode estar encoded)
        assert from_email is not None
        assert to_email == to_recipient
        assert "multipart" in message_str.lower()
        assert "Content-Type:" in message_str

    @patch("acesso_livre_api.src.admins.email_service.aiosmtplib.SMTP")
    async def test_send_email_to_correct_recipient(self, mock_smtp_class):
        """Verifica se o email é enviado para o destinatário correto."""
        mock_smtp = AsyncMock()
        mock_smtp_class.return_value.__aenter__.return_value = mock_smtp

        to_email = "specific@example.com"

        await send_password_reset_email(
            to_email=to_email, code="ABC123", reset_token="token123"
        )

        call_args = mock_smtp.sendmail.call_args
        assert to_email in call_args[0]
