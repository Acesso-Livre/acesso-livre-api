from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admins/login", auto_error=False)

def require_auth(endpoint_func):
    """Decorator para marcar endpoints que precisam de autenticação no Swagger"""
    endpoint_func._requires_auth = True
    return endpoint_func