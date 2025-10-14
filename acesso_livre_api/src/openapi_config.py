from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def create_custom_openapi(app: FastAPI):
    """
    Factory function que cria a função custom_openapi para o FastAPI.
    Captura a instância de app e devolve a função sem parâmetros esperada pelo framework.
    """
    def custom_openapi():
        """
        Configuração OpenAPI personalizada com autenticação JWT obrigatória.
        Detecta automaticamente endpoints marcados com @require_auth.
        """
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Acesso Livre API",
            version="1.0.0",
            description="API com autenticação Bearer JWT obrigatória",
            routes=app.routes,
        )
        
        # Configurar esquema de segurança Bearer obrigatório
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Token JWT obrigatório no formato: Bearer <seu_token>"
            }
        }

        # Aplicar segurança automaticamente aos endpoints marcados com @require_auth
        for route in app.routes:
            if hasattr(route, "endpoint") and hasattr(route.endpoint, "_requires_auth"):
                # Este endpoint foi marcado com @require_auth
                path_name = route.path
                if path_name in openapi_schema["paths"]:
                    path = openapi_schema["paths"][path_name]
                    for method_name, method in path.items():
                        # Garantir segurança Bearer obrigatória sem exigir token em query
                        method["security"] = [{"BearerAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return custom_openapi