import logging
from .func_log import setup_logger, log_message

from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .admins.router import router as admins_router
from .comments.router import router as comments_router
from .locations.router import router as locations_router
from .openapi_config import create_custom_openapi
from .database import engine, Base

app = FastAPI()

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Initialize logging ofrom func_log
logger = setup_logger()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manipulador para capturar erros de validação do Pydantic (422) e
    retornar uma resposta JSON estruturada e amigável.
    """
    # Verificar se há erros de path params
    has_path_errors = any("path" in str(error["loc"]) for error in exc.errors())

    if has_path_errors:
        # Retornar resposta minificada para erros de path params
        logging.error(f"Erro de validação de path params: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "detail": "Parâmetro de rota inválido",
            },
        )

    # Formato detalhado para erros de body/request
    formatted_errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if str(loc) != "body")
        message = error["msg"]
        formatted_errors.append({"field": field, "message": message})

    logging.error(f"Erro de validação de dados: {formatted_errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "detail": "Ocorreram erros de validação.",
            "errors": formatted_errors,
        },
    )


# Configuração OpenAPI obrigatória com autenticação JWT
app.openapi = create_custom_openapi(app)

app.include_router(admins_router, prefix="/api/admins", tags=["Administração"])
app.include_router(comments_router, prefix="/api/comments", tags=["Comentários"])
app.include_router(locations_router, prefix="/api/locations", tags=["Locais"])


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Status"])
def read_root():
    log_message("Logger initialized.","info")
    return {"status": "active"}