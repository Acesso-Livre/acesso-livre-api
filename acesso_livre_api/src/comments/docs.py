"""Módulo de documentação para endpoints de comentários.

Contém todas as definições de documentação OpenAPI/Swagger
para manter o código do router limpo e organizado.
"""

# Documentação para o endpoint de criação de comentário
CREATE_COMMENT_DOCS = {
    "summary": "Cria um novo comentário",
    "description": "Cria um novo comentário com nome de usuário, avaliação, texto e uma lista opcional de imagens. Também permite vincular ícones de comentário através do campo 'comment_icon_ids' (IDs separados por vírgula). O comentário é salvo com o status 'pending' por padrão.",
    "responses": {
        201: {
            "description": "Comentário criado com sucesso",
            "content": {"application/json": {"example": {"id": 1, "status": "pending"}}},
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
                        "accessibility_ids_error": {
                            "summary": "IDs de acessibilidade inválidos",
                            "value": {
                                "detail": "IDs de acessibilidade inválidos"
                            },
                        },
                        "location_id_missing": {
                            "summary": "ID da localização obrigatório",
                            "value": {
                                "detail": [
                                    {
                                        "type": "missing",
                                        "loc": ["body", "location_id"],
                                        "msg": "Field required",
                                        "input": {
                                            "user_name": "João",
                                            "rating": 5,
                                            "comment": "Bom lugar",
                                        },
                                    }
                                ]
                            },
                        },
                        "user_name_too_long": {
                            "summary": "Nome de usuário muito longo",
                            "value": {
                                "detail": [
                                    {
                                        "field": "user_name",
                                        "message": "String should have at most 30 characters",
                                    }
                                ]
                            },
                        },
                        "comment_too_long": {
                            "summary": "Comentário muito longo",
                            "value": {
                                "detail": [
                                    {
                                        "field": "comment",
                                        "message": "String should have at most 500 characters",
                                    }
                                ]
                            },
                        },
                        "rating_too_low": {
                            "summary": "Avaliação muito baixa",
                            "value": {
                                "detail": [
                                    {
                                        "field": "rating",
                                        "message": "Value should be greater than or equal to 1",
                                    }
                                ]
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
    "tags": ["Comentários"],
}

# Documentação para o endpoint de listar comentários pendentes
GET_PENDING_COMMENTS_DOCS = {
    "summary": "Lista todos os comentários pendentes",
    "description": "Endpoint protegido que requer autenticação de administrador. Retorna uma lista de comentários com status 'pending'. Se nenhum comentário pendente for encontrado, retorna uma lista vazia.",
    "responses": {
        200: {
            "description": "Lista de comentários pendentes retornada com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "comments": [
                            {
                                "id": 1,
                                "user_name": "João Silva",
                                "rating": 5,
                                "comment": "Excelente local, muito acessível!",
                                "location_id": 123,
                                "status": "pending",
                                "images": ["https://example.com/image1.jpg"],
                                "created_at": "2023-10-01T12:00:00Z",
                            },
                            {
                                "id": 2,
                                "user_name": "Maria Santos",
                                "rating": 4,
                                "comment": "Bom local, mas poderia melhorar a sinalização.",
                                "location_id": 456,
                                "status": "pending",
                                "images": [],
                                "created_at": "2023-10-02T14:30:00Z",
                            },
                        ]
                    }
                }
            },
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
    "tags": ["Comentários"],
}

# Documentação para o endpoint de atualizar status do comentário
UPDATE_COMMENT_STATUS_DOCS = {
    "summary": "Atualiza o status de um comentário",
    "description": "Endpoint protegido para administradores. Permite aprovar ou rejeitar um comentário alterando seu status. Apenas comentários com status 'pending' podem ser modificados.",
    "responses": {
        200: {
            "description": "Status do comentário atualizado com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "user_name": "João Silva",
                        "rating": 5,
                        "comment": "Excelente local, muito acessível!",
                        "location_id": 123,
                        "status": "approved",
                        "images": ["https://example.com/image1.jpg"],
                        "created_at": "2023-10-01T12:00:00Z",
                    }
                }
            },
        },
        403: {
            "description": "Acesso negado",
            "content": {
                "application/json": {
                    "example": {"detail": "Sem permissão para atualização do comentário"}
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
                                "detail": "Status 'published' não é válido. Status válidos: 'pending', 'approved', 'rejected'"
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
                "application/json": {
                    "example": {"detail": "Erro ao atualizar comentário"}
                }
            },
        },
    },
    "tags": ["Comentários"],
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
                "application/json": {"example": {"detail": "Parâmetro de rota inválido"}}
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {"example": {"detail": "Erro ao excluir comentário"}}
            },
        },
    },
    "tags": ["Comentários"],
}

# Documentação para o endpoint de obter comentário específico
GET_COMMENT_DOCS = {
    "summary": "Busca um comentário por ID",
    "description": "Recupera os detalhes de um comentário específico a partir do seu ID.",
    "responses": {
        200: {
            "description": "Detalhes do comentário retornados com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "user_name": "João Silva",
                        "rating": 5,
                        "comment": "Excelente local, muito acessível!",
                        "location_id": 123,
                        "status": "approved",
                        "images": ["https://example.com/image1.jpg"],
                        "created_at": "2023-10-01T12:00:00Z",
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
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {"example": {"detail": "Comentário não encontrado"}}
            },
        },
        422: {
            "description": "Erro de validação",
            "content": {
                "application/json": {"example": {"detail": "Parâmetro de rota inválido"}}
            },
        },
    },
    "tags": ["Comentários"],
}

# Documentação para o endpoint de listar comentários por localização
GET_COMMENTS_BY_LOCATION_DOCS = {
    "summary": "Lista comentários por ID de localização",
    "description": "Endpoint protegido que requer autenticação. Recupera uma lista paginada de comentários associados a uma localização específica, incluindo comentários com qualquer status (pending, approved, rejected). Também retorna os itens de acessibilidade do local. Suporta paginação via parâmetros 'skip' e 'limit'. Se nenhum comentário for encontrado, retorna uma lista vazia.",
    "responses": {
        200: {
            "description": "Lista de comentários e itens de acessibilidade retornada com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "comments": [
                            {
                                "id": 1,
                                "user_name": "João Silva",
                                "rating": 5,
                                "comment": "Excelente local, muito acessível!",
                                "location_id": 123,
                                "status": "approved",
                                "images": ["https://example.com/image1.jpg"],
                                "created_at": "2023-10-01T12:00:00Z",
                            },
                            {
                                "id": 2,
                                "user_name": "Maria Santos",
                                "rating": 4,
                                "comment": "Bom local, mas poderia melhorar a sinalização.",
                                "location_id": 123,
                                "status": "pending",
                                "images": [],
                                "created_at": "2023-10-02T14:30:00Z",
                            },
                        ],
                        "accessibility_items": [
                            {
                                "id": 1,
                                "name": "Bebedouro",
                                "icon_url": "https://example.com/icons/bebedouro.png",
                            },
                            {
                                "id": 2,
                                "name": "Rampa de Acesso",
                                "icon_url": "https://example.com/icons/rampa.png",
                            },
                        ]
                    }
                }
            },
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
        422: {
            "description": "Erro de validação",
            "content": {
                "application/json": {"example": {"detail": "Parâmetro de rota inválido"}}
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
    "tags": ["Comentários"],
}

# Documentação para o endpoint de listar comentários recentes
GET_RECENT_COMMENTS_DOCS = {
    "summary": "Lista os comentários mais recentes aprovados",
    "description": "Retorna uma lista dos comentários mais recentes que foram aprovados. Inclui informações sobre o local (nome e avaliação média), nome do usuário e descrição do comentário. Por padrão, retorna os 3 comentários mais recentes.",
    "responses": {
        200: {
            "description": "Lista de comentários recentes retornada com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "comments": [
                            {
                                "location_name": "Biblioteca Municipal",
                                "location_rating": 4.5,
                                "user_name": "João Silva",
                                "description": "Excelente local, muito acessível com rampas e elevadores!",
                            },
                            {
                                "location_name": "Parque Central",
                                "location_rating": 4.2,
                                "user_name": "Maria Santos",
                                "description": "Bom local, mas poderia melhorar a sinalização em braille.",
                            },
                            {
                                "location_name": "Museu de Arte",
                                "location_rating": 4.8,
                                "user_name": "Pedro Oliveira",
                                "description": "Lugar maravilhoso com excelente acessibilidade!",
                            },
                        ]
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
    "tags": ["Comentários"],
}

# Documentação para o endpoint de deletar imagem de comentário
DELETE_IMAGE_DOCS = {
    "summary": "Deleta uma imagem específica",
    "description": "Endpoint protegido para administradores. Remove permanentemente uma imagem específica. O image_id é o UUID do arquivo (nome do arquivo sem extensão), retornado na listagem de comentários. Busca automaticamente em qual comentário a imagem está.",
    "responses": {
        200: {
            "description": "Imagem excluída com sucesso",
            "content": {
                "application/json": {
                    "example": {"detail": "Image deleted successfully"}
                }
            },
        },
        403: {
            "description": "Acesso negado",
            "content": {
                "application/json": {
                    "example": {"detail": "Não autorizado"}
                }
            },
        },
        404: {
            "description": "Imagem não encontrada",
            "content": {
                "application/json": {
                    "example": {"detail": "Imagem com ID '6a9c217f-3d21-4a90-896a-2a2cb3dc53a8' não encontrada"}
                }
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao deletar imagem"}
                }
            },
        },
    },
    "tags": ["Comentários"],
}


# Documentação para gerenciamento de ícones de comentário
CREATE_COMMENT_ICON_DOCS = {
    "summary": "Cria um novo ícone de comentário",
    "description": "Cria um novo ícone de comentário que pode ser vinculado a comentários. Requer autenticação.",
    "responses": {
        201: {
            "description": "Ícone de comentário criado com sucesso",
            "content": {"application/json": {"example": {"id": 1, "name": "Ícone de Feedback"}}},
        },
        401: {
            "description": "Não autenticado",
        },
        422: {
            "description": "Erro de validação",
        },
    },
    "tags": ["Comentários - Ícones"],
}

GET_ALL_COMMENT_ICONS_DOCS = {
    "summary": "Lista todos os ícones de comentário",
    "description": "Retorna uma lista de todos os ícones de comentário disponíveis com suas URLs assinadas.",
    "responses": {
        200: {
            "description": "Lista de ícones de comentário",
            "content": {
                "application/json": {
                    "example": {
                        "comment_icons": [
                            {"id": 1, "name": "Feedback", "icon_url": "signed_url_1"},
                            {"id": 2, "name": "Sugestão", "icon_url": "signed_url_2"},
                        ]
                    }
                }
            },
        },
    },
    "tags": ["Comentários - Ícones"],
}

GET_COMMENT_ICON_BY_ID_DOCS = {
    "summary": "Obtém um ícone de comentário pelo ID",
    "description": "Retorna os detalhes de um ícone de comentário específico incluindo URL assinada.",
    "responses": {
        200: {
            "description": "Ícone encontrado",
            "content": {
                "application/json": {
                    "example": {"id": 1, "name": "Feedback", "icon_url": "signed_url"}
                }
            },
        },
        404: {
            "description": "Ícone não encontrado",
        },
    },
    "tags": ["Comentários - Ícones"],
}

DELETE_COMMENT_ICON_DOCS = {
    "summary": "Deleta um ícone de comentário",
    "description": "Remove um ícone de comentário do sistema. Requer autenticação.",
    "responses": {
        200: {
            "description": "Ícone deletado com sucesso",
            "content": {
                "application/json": {
                    "example": {"message": "Ícone deletado com sucesso"}
                }
            },
        },
        401: {
            "description": "Não autenticado",
        },
        404: {
            "description": "Ícone não encontrado",
        },
    },
    "tags": ["Comentários - Ícones"],
}

