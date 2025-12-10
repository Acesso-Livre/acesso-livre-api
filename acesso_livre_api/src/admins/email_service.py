import httpx
from ..config import settings
import logging

logger = logging.getLogger(__name__)

EMAILJS_API_URL = "https://api.emailjs.com/api/v1.0/email/send"


async def send_password_reset_email(to_email: str, code: str, reset_token: str) -> bool:
    """
    Envia email de recuperação de senha para o administrador usando EmailJS.
    
    Para envios via backend (server-side), é OBRIGATÓRIO enviar o accessToken (que é a Private Key).
    """
    reset_url = f"{settings.fronturl}/pages/admin/password-reset?email={to_email}&code={code}"

    payload = {
        "service_id": settings.emailjs_service_id,
        "template_id": settings.emailjs_template_id,
        "user_id": settings.emailjs_public_key,
        "accessToken": settings.emailjs_private_key,  
        "template_params": {
            "to_email": to_email,
            "code": code,
            "reset_url": reset_url,
        },
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                EMAILJS_API_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0,
            )

            if response.status_code == 200:
                logger.info("Email de recuperação de senha enviado para %s", to_email)
                return True
            else:
                logger.error(
                    "Erro ao enviar email para %s: Status %d - %s",
                    to_email,
                    response.status_code,
                    response.text,
                )
                raise Exception(
                    f"EmailJS error: {response.status_code} - {response.text}"
                )

    except httpx.TimeoutException as e:
        logger.error("Timeout ao enviar email para %s: %s", to_email, str(e))
        raise
    except httpx.RequestError as e:
        logger.error("Erro de requisição ao enviar email para %s: %s", to_email, str(e))
        raise
    except Exception as e:
        logger.error("Erro inesperado ao enviar email para %s: %s", to_email, str(e))
        raise
