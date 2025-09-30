# Acesso Livre API

## Visão Geral

Acesso Livre API é um projeto baseado em FastAPI, projetado para fornecer uma solução de backend robusta e escalável. Este projeto utiliza Python 3.12 e bibliotecas modernas como FastAPI e Pydantic para um desenvolvimento eficiente.

## Pré-requisitos

Antes de começar, certifique-se de ter os seguintes itens instalados:

- Python 3.12
- [Poetry](https://python-poetry.org/) para gerenciamento de dependências

## Instruções de Configuração

### 1. Clone o Repositório

```bash
git clone <repository-url>
cd acesso-livre-api
```

### 2. Crie e Configure Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e ajuste os valores conforme necessário:

```bash
cp .env.example .env
```

### 3. Instale as Dependências

Use o Poetry para instalar as dependências do projeto:

```bash
poetry install
```

### 4. Execute a Aplicação

Inicie a aplicação FastAPI:

```bash
poetry run uvicorn acesso_livre_api.src.main:app --reload
```

## 🗄️ Modelo de Dados

```mermaid
erDiagram
    LOCATIONS ||--o{ COMMENTS : "possui"
    LOCATIONS ||--o{ LOCATION_ACCESSIBILITY : "através de"
    LOCATION_ACCESSIBILITY }o--|| ACCESSIBILITY_ITEMS : "referencia"
    COMMENTS }o--|| ADMINS : "aprovado_por"

    LOCATIONS {
        int id PK
        string name
        string description
        text images
        float avg_rating
        datetime created_at
        datetime updated_at
    }

    COMMENTS {
        int id PK
        string user_name
        int rating
        string comment
        datetime created_at
        text images
        string status
        int location_id FK
        int approved_by FK "nullable"
    }

    ACCESSIBILITY_ITEMS {
        int id PK
        string name
        string icon_url
    }

    LOCATION_ACCESSIBILITY {
        int location_id FK
        int item_id FK
    }

    ADMINS {
        int id PK
        string email
        string password
        string reset_token_hash "nullable"
        datetime reset_token_expires "nullable"
        datetime created_at
        datetime updated_at
    }
```
