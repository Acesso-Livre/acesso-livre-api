"""Módulo de documentação para endpoints de comentários.

Contém todas as definições de documentação OpenAPI/Swagger
para manter o código do router limpo e organizado.
"""

# Documentação para o endpoint de criação de comentário
CREATE_COMMENT_DOCS = {
    "summary": "Cria um novo comentário",
    "description": "Cria um novo comentário com nome de usuário, avaliação, texto e uma lista opcional de imagens. O comentário é salvo com o status 'pending' por padrão.",
    "responses": {
        201: {
            "description": "Comentário criado com sucesso",
            "content": {
                "application/json": {
                    "example": {"id": 1, "status": "pending"}
                }
            },
        },
        422: {
            "description": "Erro de validação nos dados enviados",
            "content": {
                "application/json": {
                    "examples": {
                        "rating_error": {
                            "summary": "Avaliação inválida",
                            "value": {
                                "detail": "Avaliação 6 está fora do range válido. Avaliações devem estar entre 1 e 5"
                            },
                        },
                        "image_error": {
                            "summary": "Imagens inválidas",
                            "value": {
                                "detail": "Problema com imagens: Uma ou mais imagens têm formato inválido"
                            },
                        },
                    }
                }
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Erro interno ao processar criação do comentário"
                    }
                }
            },
        },
    },
    "tags": ["comments"],
    "status_code": 201,
}

# Documentação para o endpoint de listar comentários pendentes
GET_PENDING_COMMENTS_DOCS = {
    "summary": "Lista todos os comentários pendentes",
    "description": "Endpoint protegido que requer autenticação de administrador. Retorna uma lista de comentários com status 'pending'. Se nenhum comentário pendente for encontrado, retorna uma lista vazia.",
    "responses": {
        200: {
            "description": "Lista de comentários pendentes retornada com sucesso.",
        },
        403: {
            "description": "Acesso negado",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Sem permissão para realizar esta operação no comentário"
                    }
                }
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Ocorreu um erro interno no processamento dos comentários."
                    }
                }
            },
        },
    },
    "tags": ["comments"],
}

# Documentação para o endpoint de atualizar status do comentário
UPDATE_COMMENT_STATUS_DOCS = {
    "summary": "Atualiza o status de um comentário",
    "description": "Endpoint protegido para administradores. Permite aprovar ou rejeitar um comentário alterando seu status. Apenas comentários com status 'pending' podem ser modificados.",
    "responses": {
        200: {
            "description": "Status do comentário atualizado com sucesso.",
        },
        403: {
            "description": "Acesso negado",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Sem permissão para atualização do comentário"
                    }
                }
            },
        },
        404: {
            "description": "Comentário não encontrado",
            "content": {
                "application/json": {"example": {"detail": "Comentário não encontrado"}}
            },
        },
        422: {
            "description": "Erro de validação",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_status": {
                            "summary": "Status inválido",
                            "value": {
                                "detail": "Status 'published' não é válido. Status válidos:  'approved', 'rejected'"
                            },
                        },
                        "not_pending": {
                            "summary": "Comentário não está pendente",
                            "value": {
                                "detail": "Comentário 1 não pode ser processado pois está com status 'approved'. Apenas comentários com status 'pending' podem ser aprovados ou rejeitados"
                            },
                        },
                    }
                }
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {"example": {"detail": "Erro ao atualizar comentário"}}
            },
        },
    },
    "tags": ["comments"],
}

# Documentação para o endpoint de deletar comentário
DELETE_COMMENT_DOCS = {
    "summary": "Exclui um comentário",
    "description": "Endpoint protegido para administradores. Remove permanentemente um comentário do banco de dados.",
    "responses": {
        200: {
            "description": "Comentário excluído com sucesso",
            "content": {
                "application/json": {
                    "example": {"detail": "Comment deleted successfully"}
                }
            },
        },
        403: {
            "description": "Acesso negado",
            "content": {
                "application/json": {
                    "example": {"detail": "Sem permissão para excluir do comentário"}
                }
            },
        },
        404: {
            "description": "Comentário não encontrado",
            "content": {
                "application/json": {"example": {"detail": "Comentário não encontrado"}}
            },
        },
        422: {
            "description": "Erro de validação",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["path", "comment_id"],
                                "msg": "value is not a valid integer",
                                "type": "type_error.integer",
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {"example": {"detail": "Erro ao excluir comentário"}}
            },
        },
    },
    "tags": ["comments"],
}

# Documentação para o endpoint de obter comentário específico
GET_COMMENT_DOCS = {
    "summary": "Busca um comentário por ID",
    "description": "Recupera os detalhes de um comentário específico a partir do seu ID.",
    "responses": {
        200: {
            "description": "Detalhes do comentário.",
        },
        404: {
            "description": "Comentário não encontrado",
            "content": {
                "application/json": {"example": {"detail": "Comentário não encontrado"}}
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {
                    "example": {"detail": "Comentário não encontrado"}
                }
            },
        },
        422: {
            "description": "Erro de validação",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["path", "comment_id"],
                                "msg": "value is not a valid integer",
                                "type": "type_error.integer",
                            }
                        ]
                    }
                }
            },
        },
    },
    "tags": ["comments"],
}