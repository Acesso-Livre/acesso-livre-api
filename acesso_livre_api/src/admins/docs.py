"""
Módulo de documentação para endpoints de administradores.

Contém todas as definições de documentação OpenAPI/Swagger
para manter o código do router limpo e organizado.
"""

from typing import Dict, Any

# Documentação para o endpoint de registro
REGISTER_DOCS = {
    "summary": "Registrar novo administrador",
    "responses": {
        201: {
            "description": "Administrador criado com sucesso",
            "content": {
                "application/json": {
                    "example": {"status": "success"}
                }
            }
        },
        400: {
            "description": "Dados inválidos",
            "content": {
                "application/json": {
                    "examples": {
                        "email_exists": {
                            "summary": "Email já cadastrado",
                            "value": {"detail": "Email já cadastrado"}
                        },
                        "weak_password": {
                            "summary": "Senha muito fraca",
                            "value": {"detail": "A senha deve ter pelo menos 8 caracteres, incluindo letra maiúscula, minúscula, número e caractere especial."}
                        }
                    }
                }
            }
        }
    },
    "tags": ["Administração"]
}

# Documentação para o endpoint de login
LOGIN_DOCS = {
    "summary": "Login de administrador",
    "responses": {
        200: {
            "description": "Login realizado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBlbXByZXNhLmNvbSIsImV4cCI6MTYzODUwMDAwMH0.signature",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Credenciais inválidas",
            "content": {
                "application/json": {
                    "example": {"detail": "Credenciais inválidas"}
                }
            }
        }
    },
    "tags": ["Administração"]
}

# Documentação para o endpoint de verificação de token
CHECK_TOKEN_DOCS = {
    "summary": "Verificar validade do token",
    "responses": {
        200: {
            "description": "Status do token",
            "content": {
                "application/json": {
                    "examples": {
                        "valid": {
                            "summary": "Token válido",
                            "value": {"valid": True}
                        },
                        "invalid": {
                            "summary": "Token inválido",
                            "value": {"valid": False, "message": "Token inválido ou expirado"}
                        },
                        "missing": {
                            "summary": "Token não fornecido",
                            "value": {"valid": False, "message": "Token não fornecido"}
                        }
                    }
                }
            }
        },
        401: {
            "description": "Token inválido ou não fornecido",
            "content": {
                "application/json": {
                    "example": {"detail": "Token inválido"}
                }
            }
        }
    },
    "tags": ["Administração"]
}

# Documentação para o endpoint de esqueci senha
FORGOT_PASSWORD_DOCS = {
    "summary": "Solicitar recuperação de senha",
    "responses": {
        200: {
            "description": "Código de recuperação enviado",
            "content": {
                "application/json": {
                    "example": {"message": "Enviamos um link de recuperação ao email."}
                }
            }
        },
        404: {
            "description": "Email não encontrado",
            "content": {
                "application/json": {
                    "example": {"detail": "Administrador não encontrado"}
                }
            }
        }
    },
    "tags": ["Administração"]
}

# Documentação para o endpoint de redefinição de senha
PASSWORD_RESET_DOCS = {
    "summary": "Redefinir senha",
    "responses": {
        200: {
            "description": "Senha redefinida com sucesso",
            "content": {
                "application/json": {
                    "example": {"message": "Senha atualizada com sucesso!"}
                }
            }
        },
        400: {
            "description": "Dados inválidos",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_code": {
                            "summary": "Código inválido",
                            "value": {"detail": "Código inválido"}
                        },
                        "expired_code": {
                            "summary": "Código expirado",
                            "value": {"detail": "Código de recuperação expirado"}
                        },
                        "weak_password": {
                            "summary": "Senha fraca",
                            "value": {"detail": "A senha deve ter pelo menos 8 caracteres, incluindo letra maiúscula, minúscula, número e caractere especial."}
                        }
                    }
                }
            }
        },
        404: {
            "description": "Email não encontrado",
            "content": {
                "application/json": {
                    "example": {"detail": "Administrador não encontrado"}
                }
            }
        }
    },
    "tags": ["Administração"]
}