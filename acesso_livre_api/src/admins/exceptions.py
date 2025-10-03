from fastapi import HTTPException, status
from typing import Optional

class AdminException(HTTPException):
    """Classe base para todas as exceções do módulo de admins"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers,
        )

class AdminAlreadyExistsException(AdminException):
    """Exceção levantada quando tenta criar um admin com email já existente"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Administrador com este email já existe",
        )




class AdminCreationException(AdminException):
    """Exceção levantada quando ocorre erro geral na criação do admin"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar solicitação",
        )


class AdminNotFoundException(AdminException):
    """Exceção levantada quando um admin não é encontrado"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Administrador não encontrado",
        )


class AdminAuthenticationFailedException(AdminException):
    """Exceção levantada quando a autenticação do admin falha"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

class AdminInvalidEmailException(AdminException):
    """Exceção levantada quando o email do admin é inválido"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O email fornecido não é válido",
        )


class AdminWeakPasswordException(AdminException):
    """Exceção levantada quando a senha não atende aos requisitos mínimos"""

    def __init__(
        self,
        message: str = (
            "A senha deve ter pelo menos 8 caracteres, incluindo letra maiúscula, "
            "minúscula, número e caractere especial."
        ),
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


class InvalidResetTokenException(AdminException):
    """Exceção levantada quando o token de reset de senha é inválido"""

    def __init__(self, reason: str = "Token inválido"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reason,
        )


class ExpiredResetTokenException(AdminException):
    """Exceção levantada quando o token de reset de senha está expirado"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de recuperação de senha expirado",
        )


class ResetTokenAlreadyUsedException(AdminException):
    """Exceção levantada quando o token de reset de senha já foi usado"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de recuperação já utilizado",
        )