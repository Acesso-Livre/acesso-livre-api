import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config import settings
import logging
from ..func_log import log_message


logger = logging.getLogger(__name__)

def create_password_reset_email_body(email: str, code: str, reset_token: str) -> str:
    """
    Cria o corpo do email HTML para reset de senha.
    """
    reset_url = f"{settings.api}/admins/password-reset?email={email}&code={code}&token={reset_token}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #007bff;
                color: white;
                padding: 20px;
                border-radius: 5px 5px 0 0;
                text-align: center;
            }}
            .content {{
                padding: 20px;
            }}
            .reset-link {{
                display: inline-block;
                background-color: #007bff;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .code {{
                background-color: #e9ecef;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                font-size: 14px;
                text-align: center;
                margin: 15px 0;
            }}
            .footer {{
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
            }}
            .warning {{
                background-color: #fff3cd;
                border: 1px solid #ffc107;
                color: #856404;
                padding: 10px;
                border-radius: 5px;
                margin: 15px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Recuperação de Senha - Acesso Livre</h2>
            </div>
            <div class="content">
                <p>Olá,</p>
                <p>Recebemos uma solicitação para redefinir a senha da sua conta. Se você não fez essa solicitação, 
                ignore este email.</p>
                
                <p>Para redefinir sua senha, clique no botão abaixo ou use o código de recuperação:</p>
                
                <center>
                    <a href="{reset_url}" class="reset-link">Redefinir Senha</a>
                </center>
                
                <p>Ou use este código de recuperação:</p>
                <div class="code">{code}</div>
                
                <div class="warning">
                    <strong>Atenção:</strong> Este link expirará em 15 minutos. Se ele tiver expirado, 
                    solicite uma nova recuperação de senha.
                </div>
                
                <p>Se você tiver dúvidas ou não solicitou esta recuperação, entre em contato com o suporte.</p>
            </div>
            <div class="footer">
                <p>Este é um email automático, por favor não responda.</p>
                <p>&copy; 2024 Acesso Livre. Todos os direitos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """
    log_message("HTML de e-mail de recuperação criado.", level="debug")
    return html_body


async def send_password_reset_email(to_email: str, code: str, reset_token: str) -> bool:
    """
    Envia email de recuperação de senha para o administrador.
    """
    try:

        message = MIMEMultipart("alternative")
        message["Subject"] = "Recuperação de Senha - Acesso Livre"
        message["From"] = settings.sender_email
        message["To"] = to_email

        text_body = f"""
        Recuperação de Senha - Acesso Livre
        
        Olá,
        
        Recebemos uma solicitação para redefinir a senha da sua conta.
        
        Código de recuperação: {code}
        
        Este código expirará em 15 minutos.
        
        Se você não solicitou esta recuperação, ignore este email.
        
        ---
        Este é um email automático, por favor não responda.
        """

        html_body = create_password_reset_email_body(to_email, code, reset_token)

        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
        message.attach(part1)
        message.attach(part2)

        # Conectar ao servidor SMTP com STARTTLS
        async with aiosmtplib.SMTP(
            hostname=settings.smtp_server,
            port=settings.smtp_port,
            use_tls=False,
            start_tls=True,
        ) as smtp:
            await smtp.login(settings.smtp_user, settings.smtp_password)
            await smtp.sendmail(settings.sender_email, to_email, message.as_string())

        logger.info("Email de recuperação de senha enviado para %s", to_email)
        log_message("Email de recuperação de senha enviado com sucesso.", level="info")
        return True

    except aiosmtplib.SMTPException as e:
        logger.error("Erro SMTP ao enviar email para %s: %s", to_email, str(e))
        log_message("Erro SMTP ao enviar email de recuperação.", level="error")
        log_message(str(e), level="error")
        raise
    except Exception as e:
        logger.error("Erro inesperado ao enviar email para %s: %s", to_email, str(e))
        log_message("Erro inesperado ao enviar email de recuperação.", level="error")
        log_message(str(e), level="error")
        raise
        