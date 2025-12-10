from unittest.mock import Mock, AsyncMock, MagicMock, patch
import pytest
from sqlalchemy.exc import SQLAlchemyError

from acesso_livre_api.src.comments.exceptions import CommentGenericException
from acesso_livre_api.src.comments.service import get_recent_comments


@pytest.fixture
def mock_db():
    """Mock do banco de dados como AsyncSession-like."""
    m = AsyncMock()
    m.execute = AsyncMock()
    return m


@pytest.fixture
def sample_location():
    """Dados de exemplo para localização."""
    location = Mock()
    location.id = 1
    location.name = "Biblioteca Municipal"
    location.avg_rating = 4.5
    location.description = "Uma biblioteca acessível"
    return location


@pytest.fixture
def sample_comment(sample_location):
    """Dados de exemplo para comentário."""
    comment = Mock()
    comment.id = 1
    comment.user_name = "João Silva"
    comment.rating = 5
    comment.comment = "Excelente local, muito acessível!"
    comment.location_id = 1
    comment.status = "approved"
    comment.created_at = "2023-10-01T12:00:00Z"
    comment.location = sample_location
    comment.images = []
    comment.icon_url = None
    return comment


class TestGetRecentComments:
    """Testes para get_recent_comments."""

    @pytest.mark.asyncio
    
    @patch("acesso_livre_api.src.comments.service.get_signed_urls")
    async def test_get_recent_comments_success(self, mock_get_signed_urls, mock_db, sample_comment):
        """Testa obtenção bem-sucedida de comentários recentes."""
        mock_get_signed_urls.return_value = []
        
        # Mock do execute retornando um result object
        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [
            sample_comment
        ]
        mock_db.execute.return_value = mock_result

        result = await get_recent_comments(mock_db, limit=3)

        assert len(result) == 1
        assert result[0].user_name == "João Silva"
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_recent_comments_returns_empty_list(self, mock_db):
        """Testa quando não há comentários recentes."""
        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await get_recent_comments(mock_db, limit=3)

        assert result == []

    @pytest.mark.asyncio
    
    @patch("acesso_livre_api.src.comments.service.get_signed_urls")
    async def test_get_recent_comments_with_multiple_comments(
        self, mock_get_signed_urls, mock_db, sample_comment
    ):
        """Testa obtenção de múltiplos comentários recentes."""
        mock_get_signed_urls.return_value = []
        
        comment2 = Mock()
        comment2.user_name = "Maria Santos"
        comment2.comment = "Bom local!"
        comment2.images = []
        comment2.icon_url = None

        comment3 = Mock()
        comment3.user_name = "Pedro Oliveira"
        comment3.comment = "Maravilhoso!"
        comment3.images = []
        comment3.icon_url = None

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [
            sample_comment,
            comment2,
            comment3,
        ]
        mock_db.execute.return_value = mock_result

        result = await get_recent_comments(mock_db, limit=5)

        assert len(result) == 3
        assert result[0].user_name == "João Silva"
        assert result[1].user_name == "Maria Santos"
        assert result[2].user_name == "Pedro Oliveira"

    @pytest.mark.asyncio
    async def test_get_recent_comments_database_error(self, mock_db):
        """Testa tratamento de erro de banco de dados."""
        mock_db.execute.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(CommentGenericException):
            await get_recent_comments(mock_db, limit=3)

    @pytest.mark.asyncio
    async def test_get_recent_comments_generic_error(self, mock_db):
        """Testa tratamento de erro genérico."""
        mock_db.execute.side_effect = Exception("Unexpected error")

        with pytest.raises(CommentGenericException):
            await get_recent_comments(mock_db, limit=3)

    @pytest.mark.asyncio
    
    @patch("acesso_livre_api.src.comments.service.get_signed_urls")
    async def test_get_recent_comments_respects_limit(self, mock_get_signed_urls, mock_db, sample_comment):
        """Testa se a função respeita o parâmetro limit."""
        mock_get_signed_urls.return_value = []
        
        # Criar múltiplos comentários
        comments = [sample_comment for _ in range(10)]

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = comments[
            :5
        ]
        mock_db.execute.return_value = mock_result

        result = await get_recent_comments(mock_db, limit=5)

        assert len(result) == 5

    @pytest.mark.asyncio
    
    @patch("acesso_livre_api.src.comments.service.get_signed_urls")
    async def test_get_recent_comments_default_limit(self, mock_get_signed_urls, mock_db, sample_comment):
        """Testa se o limite padrão é 3."""
        mock_get_signed_urls.return_value = []
        
        comments = [sample_comment for _ in range(3)]

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = comments
        mock_db.execute.return_value = mock_result

        result = await get_recent_comments(mock_db)

        assert len(result) == 3

    @pytest.mark.asyncio
    
    @patch("acesso_livre_api.src.comments.service.get_signed_urls")
    async def test_get_recent_comments_includes_location(
        self, mock_get_signed_urls, mock_db, sample_comment, sample_location
    ):
        """Testa se os comentários incluem informações de localização."""
        mock_get_signed_urls.return_value = []
        
        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [
            sample_comment
        ]
        mock_db.execute.return_value = mock_result

        result = await get_recent_comments(mock_db, limit=3)

        assert len(result) == 1
        assert result[0].location is not None
        assert result[0].location.name == "Biblioteca Municipal"
        assert result[0].location.avg_rating == 4.5

    @pytest.mark.asyncio
    
    @patch("acesso_livre_api.src.comments.service.get_signed_urls")
    async def test_get_recent_comments_with_icon_urls(
        self, mock_get_signed_urls, mock_db, sample_comment
    ):
        """Testa se múltiplos comentários com icon_url têm URLs assinadas corretamente."""
        def mock_get_signed_urls_impl(urls):
            return [f"signed_{url}" for url in urls]
        
        mock_get_signed_urls.side_effect = mock_get_signed_urls_impl
        

        comment1 = Mock()
        comment1.user_name = "João Silva"
        comment1.images = []
        comment1.icon_url = "icon1.jpg"
        comment1.status = "approved"

        comment2 = Mock()
        comment2.user_name = "Maria Santos"
        comment2.images = []
        comment2.icon_url = "icon2.jpg"
        comment2.status = "approved"

        comment3 = Mock()
        comment3.user_name = "Pedro Oliveira"
        comment3.images = []
        comment3.icon_url = None
        comment3.status = "approved"

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [
            comment1,
            comment2,
            comment3,
        ]
        mock_db.execute.return_value = mock_result

        result = await get_recent_comments(mock_db, limit=5)

        assert len(result) == 3
        assert result[0].icon_url == "signed_icon1.jpg"
        assert result[1].icon_url == "signed_icon2.jpg"
        assert result[2].icon_url is None
