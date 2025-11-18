"""Módulo de documentação para endpoints de locations.

Contém todas as definições de documentação OpenAPI/Swagger
para manter o código do router limpo e organizado.
"""

# Documentação para o endpoint POST / (criar location)
CREATE_LOCATION_DOCS = {
    "summary": "Criar novo local",
    "description": "Cria um novo local com coordenadas top e left para posicionamento no mapa.",
    "status_code": 201,
    "responses": {
        201: {
            "description": "Local criado com sucesso",
            "content": {"application/json": {"example": {"id": 1}}},
        },
        401: {
            "description": "Token de autenticação obrigatório",
            "content": {
                "application/json": {
                    "example": {"detail": "Token de autenticação obrigatório"}
                }
            },
        },
        422: {
            "description": "Erro de validação",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_fields": {
                            "summary": "Campos obrigatórios faltando",
                            "value": {
                                "detail": [
                                    {"field": "name", "message": "Field required"},
                                    {"field": "description", "message": "Field required"},
                                ]
                            },
                        },
                        "invalid_name": {
                            "summary": "Nome muito longo",
                            "value": {
                                "detail": [
                                    {
                                        "field": "name",
                                        "message": "String should have at most 200 characters",
                                    }
                                ]
                            },
                        },
                        "name_too_short": {
                            "summary": "Nome vazio ou muito curto",
                            "value": {
                                "detail": [
                                    {
                                        "field": "name",
                                        "message": "String should have at least 1 character",
                                    }
                                ]
                            },
                        },
                        "description_empty": {
                            "summary": "Descrição vazia",
                            "value": {
                                "detail": [
                                    {"field": "description", "message": "Field required"}
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
                "application/json": {"example": {"detail": "Erro interno do servidor"}}
            },
        },
    },
}

# Documentação para o endpoint GET / (listar locations)
LIST_LOCATIONS_DOCS = {
    "summary": "Listar locais",
    "description": "Retorna uma lista paginada de locais com suas coordenadas top e left.",
    "responses": {
        200: {
            "description": "Lista de locais retornada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "locations": [
                            {
                                "id": 1,
                                "name": "Shopping Center Norte",
                                "description": "Grande centro comercial com acesso para cadeirantes",
                                "top": 45.2,
                                "left": 120.8,
                            },
                            {
                                "id": 2,
                                "name": "Praça Central",
                                "description": "Praça pública com rampas de acesso",
                                "top": 78.5,
                                "left": 95.3,
                            },
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {"example": {"detail": "Erro interno do servidor"}}
            },
        },
    },
}

# Documentação para o endpoint GET /{location_id} (obter location por ID)
GET_LOCATION_DOCS = {
    "summary": "Obter local por ID",
    "description": "Retorna os detalhes completos de um local específico incluindo itens de acessibilidade.",
    "responses": {
        200: {
            "description": "Local encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Shopping Center Norte",
                        "description": "Grande centro comercial com acesso para cadeirantes",
                        "images": [
                            "https://example.com/image1.jpg",
                            "https://example.com/image2.jpg",
                        ],
                        "avg_rating": 4.2,
                        "top": 45.2,
                        "left": 120.8,
                        "accessibility_items": [
                            {
                                "id": 1,
                                "name": "Rampa de acesso",
                                "icon_url": "https://example.com/ramp-icon.svg",
                            },
                            {
                                "id": 2,
                                "name": "Elevador",
                                "icon_url": "https://example.com/elevator-icon.svg",
                            },
                        ],
                    }
                }
            },
        },
        404: {
            "description": "Local não encontrado",
            "content": {
                "application/json": {"example": {"detail": "Local não encontrado"}}
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {"example": {"detail": "Erro interno do servidor"}}
            },
        },
    },
}

# Documentação para o endpoint PATCH /{location_id} (atualizar location)
UPDATE_LOCATION_DOCS = {
    "summary": "Atualizar local",
    "description": "Atualiza parcialmente um local existente. Apenas os campos fornecidos serão atualizados.",
    "responses": {
        200: {
            "description": "Local atualizado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Shopping Center Norte Atualizado",
                        "description": "Grande centro comercial com acesso para cadeirantes - reformado",
                        "images": ["https://example.com/image1.jpg"],
                        "avg_rating": 4.2,
                        "top": 50.0,
                        "left": 125.0,
                        "accessibility_items": [
                            {
                                "id": 1,
                                "name": "Rampa de acesso",
                                "icon_url": "https://example.com/ramp-icon.svg",
                            }
                        ],
                    }
                }
            },
        },
        401: {
            "description": "Token de autenticação obrigatório",
            "content": {
                "application/json": {
                    "example": {"detail": "Token de autenticação obrigatório"}
                }
            },
        },
        404: {
            "description": "Local não encontrado",
            "content": {
                "application/json": {"example": {"detail": "Local não encontrado"}}
            },
        },
        422: {
            "description": "Erro de validação",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "field": "name",
                                "message": "String should have at most 200 characters",
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {"example": {"detail": "Erro interno do servidor"}}
            },
        },
    },
}

# Documentação para o endpoint DELETE /{location_id} (deletar location)
DELETE_LOCATION_DOCS = {
    "summary": "Deletar local",
    "description": "Remove um local do sistema permanentemente.",
    "responses": {
        200: {
            "description": "Local deletado com sucesso",
            "content": {
                "application/json": {"example": {"message": "Local deletado com sucesso"}}
            },
        },
        401: {
            "description": "Token de autenticação obrigatório",
            "content": {
                "application/json": {
                    "example": {"detail": "Token de autenticação obrigatório"}
                }
            },
        },
        404: {
            "description": "Local não encontrado",
            "content": {
                "application/json": {"example": {"detail": "Local não encontrado"}}
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {"example": {"detail": "Erro interno do servidor"}}
            },
        },
    },
}

# Documentação para o endpoint POST /accessibility-items/ (criar accessibility item)
CREATE_ACCESSIBILITY_ITEM_DOCS = {
    "summary": "Criar item de acessibilidade",
    "description": "Cria um novo item de acessibilidade que pode ser associado a locais.",
    "responses": {
        201: {
            "description": "Item de acessibilidade criado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Rampa de acesso",
                        "icon_url": "https://example.com/ramp-icon.svg",
                    }
                }
            },
        },
        401: {
            "description": "Token de autenticação obrigatório",
            "content": {
                "application/json": {
                    "example": {"detail": "Token de autenticação obrigatório"}
                }
            },
        },
        422: {
            "description": "Erro de validação",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"field": "name", "message": "Field required"},
                            {"field": "icon_url", "message": "Field required"},
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {"example": {"detail": "Erro interno do servidor"}}
            },
        },
    },
}

# Documentação para o endpoint GET /accessibility-items/ (listar accessibility items)
LIST_ACCESSIBILITY_ITEMS_DOCS = {
    "summary": "Listar itens de acessibilidade",
    "description": "Retorna uma lista de todos os itens de acessibilidade disponíveis.",
    "responses": {
        200: {
            "description": "Lista de itens de acessibilidade",
            "content": {
                "application/json": {
                    "example": {
                        "accessibility_items": [
                            {
                                "id": 1,
                                "name": "Rampa de acesso",
                                "icon_url": "https://example.com/ramp-icon.svg",
                            },
                            {
                                "id": 2,
                                "name": "Elevador",
                                "icon_url": "https://example.com/elevator-icon.svg",
                            },
                            {
                                "id": 3,
                                "name": "Banheiro acessível",
                                "icon_url": "https://example.com/bathroom-icon.svg",
                            },
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {"example": {"detail": "Erro interno do servidor"}}
            },
        },
    },
}

# Documentação para o endpoint GET /accessibility-items/{item_id} (obter accessibility item por ID)
GET_ACCESSIBILITY_ITEM_DOCS = {
    "summary": "Obter item de acessibilidade por ID",
    "description": "Retorna os detalhes de um item de acessibilidade específico.",
    "responses": {
        200: {
            "description": "Item de acessibilidade encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Rampa de acesso",
                        "icon_url": "https://example.com/ramp-icon.svg",
                    }
                }
            },
        },
        404: {
            "description": "Item de acessibilidade não encontrado",
            "content": {
                "application/json": {
                    "example": {"detail": "Item de acessibilidade não encontrado"}
                }
            },
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {"example": {"detail": "Erro interno do servidor"}}
            },
        },
    },
}
