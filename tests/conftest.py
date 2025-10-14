import pytest
import os

@pytest.fixture(scope='session', autouse=True)
def set_test_environment_variables():
    """
    Define variáveis de ambiente fictícias para a sessão de testes.
    
    Isso previne o erro de validação do Pydantic ao carregar as configurações
    durante a coleta de testes, garantindo que o módulo de configuração
    possa ser importado sem depender do ambiente de execução.
    """
    os.environ['API'] = "Acesso Livre API"
    os.environ['DATABASE_URL'] = "postgresql://test:test@localhost/testdb"
    os.environ['SECRET_KEY'] = "test-secret-key"
    os.environ['ALGORITHM'] = "HS256"
    os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = "30"
    os.environ['RESET_TOKEN_EXPIRE_MINUTES'] = "15"
