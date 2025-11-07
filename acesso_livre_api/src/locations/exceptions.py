from fastapi import HTTPException, status


class LocationException(HTTPException):
    """Classe base para todas as exceções do módulo de locations"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers,
        )


class LocationNotFoundException(LocationException):
    """Exceção lançada quando uma location não é encontrada"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Localização não encontrada",
        )


class LocationCreateException(LocationException):
    """Exceção lançada quando ocorre erro geral na criação da localização"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar criação da localização",
        )


class LocationUpdateException(LocationException):
    """Exceção lançada quando ocorre erro geral na atualização da localização"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar atualização da localização",
        )


class LocationDeleteException(LocationException):
    """Exceção lançada quando ocorre erro geral na exclusão da localização"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar exclusão da localização",
        )


class LocationGenericException(LocationException):
    """Exceção genérica para erros internos no módulo de locations"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro interno no processamento das localizações",
        )


class AccessibilityItemNotFoundException(LocationException):
    """Exceção lançada quando um item de acessibilidade não é encontrado"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item de acessibilidade não encontrado",
        )


class AccessibilityItemCreateException(LocationException):
    """Exceção lançada quando ocorre erro geral na criação do item de acessibilidade"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar criação do item de acessibilidade",
        )


class AccessibilityItemGenericException(LocationException):
    """Exceção genérica para erros internos no processamento dos itens de acessibilidade"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no processamento dos itens de acessibilidade",
        )