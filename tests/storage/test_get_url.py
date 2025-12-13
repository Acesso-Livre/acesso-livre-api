"""Testes unitários para o cache de signed URLs."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from acesso_livre_api.storage.get_url import (
    get_signed_url,
    get_signed_urls,
    _url_cache,
    _cache_lock,
)


@pytest.fixture(autouse=True)
def clear_cache():
    """Limpa o cache antes e depois de cada teste."""
    _url_cache.clear()
    yield
    _url_cache.clear()


class TestGetSignedUrlCache:
    """Testes para o cache de signed URLs."""

    @pytest.mark.asyncio
    async def test_cache_miss_calls_supabase(self):
        """Testa que cache miss faz chamada ao Supabase."""
        with patch("acesso_livre_api.storage.get_url.supabase_client") as mock_client:
            mock_storage = MagicMock()
            mock_storage.create_signed_url.return_value = {"signedURL": "https://signed-url.com/image.jpg"}
            mock_client.return_value.storage.from_.return_value = mock_storage

            result = await get_signed_url("test_image.jpg")

            assert result == "https://signed-url.com/image.jpg"
            mock_storage.create_signed_url.assert_called_once_with("test_image.jpg", 3600)

    @pytest.mark.asyncio
    async def test_cache_hit_skips_supabase(self):
        """Testa que cache hit não faz chamada ao Supabase."""
        with patch("acesso_livre_api.storage.get_url.supabase_client") as mock_client:
            mock_storage = MagicMock()
            mock_storage.create_signed_url.return_value = {"signedURL": "https://signed-url.com/image.jpg"}
            mock_client.return_value.storage.from_.return_value = mock_storage

            # Primeira chamada - cache miss
            result1 = await get_signed_url("cached_image.jpg")
            
            # Segunda chamada - cache hit
            result2 = await get_signed_url("cached_image.jpg")

            assert result1 == result2
            # Supabase deve ser chamado apenas UMA vez
            assert mock_storage.create_signed_url.call_count == 1

    @pytest.mark.asyncio
    async def test_different_files_different_cache_entries(self):
        """Testa que arquivos diferentes têm entradas de cache separadas."""
        with patch("acesso_livre_api.storage.get_url.supabase_client") as mock_client:
            mock_storage = MagicMock()
            mock_storage.create_signed_url.side_effect = [
                {"signedURL": "https://url1.com"},
                {"signedURL": "https://url2.com"},
            ]
            mock_client.return_value.storage.from_.return_value = mock_storage

            result1 = await get_signed_url("image1.jpg")
            result2 = await get_signed_url("image2.jpg")

            assert result1 == "https://url1.com"
            assert result2 == "https://url2.com"
            assert mock_storage.create_signed_url.call_count == 2

    @pytest.mark.asyncio
    async def test_different_expires_in_different_cache_entries(self):
        """Testa que expires_in diferentes criam entradas de cache separadas."""
        with patch("acesso_livre_api.storage.get_url.supabase_client") as mock_client:
            mock_storage = MagicMock()
            mock_storage.create_signed_url.side_effect = [
                {"signedURL": "https://url-3600.com"},
                {"signedURL": "https://url-7200.com"},
            ]
            mock_client.return_value.storage.from_.return_value = mock_storage

            result1 = await get_signed_url("image.jpg", expires_in=3600)
            result2 = await get_signed_url("image.jpg", expires_in=7200)

            assert result1 == "https://url-3600.com"
            assert result2 == "https://url-7200.com"
            assert mock_storage.create_signed_url.call_count == 2

    @pytest.mark.asyncio
    async def test_cache_stores_url_correctly(self):
        """Testa que a URL é armazenada corretamente no cache."""
        with patch("acesso_livre_api.storage.get_url.supabase_client") as mock_client:
            mock_storage = MagicMock()
            mock_storage.create_signed_url.return_value = {"signedURL": "https://cached.com"}
            mock_client.return_value.storage.from_.return_value = mock_storage

            await get_signed_url("store_test.jpg")

            cache_key = "store_test.jpg:3600"
            assert cache_key in _url_cache
            assert _url_cache[cache_key] == "https://cached.com"


class TestGetSignedUrlsCache:
    """Testes para get_signed_urls com cache."""

    @pytest.mark.asyncio
    async def test_multiple_urls_uses_cache(self):
        """Testa que múltiplas URLs usam o cache corretamente."""
        with patch("acesso_livre_api.storage.get_url.supabase_client") as mock_client:
            mock_storage = MagicMock()
            call_count = [0]
            
            def mock_create_signed_url(path, expires):
                call_count[0] += 1
                return {"signedURL": f"https://url-{path}"}
            
            mock_storage.create_signed_url.side_effect = mock_create_signed_url
            mock_client.return_value.storage.from_.return_value = mock_storage

            file_paths = ["img1.jpg", "img2.jpg", "img3.jpg"]
            
            # Primeira chamada
            results1 = await get_signed_urls(file_paths)
            first_call_count = call_count[0]
            
            # Segunda chamada - deve usar cache
            results2 = await get_signed_urls(file_paths)

            assert len(results1) == 3
            assert results1 == results2
            # Deve ter chamado Supabase apenas 3 vezes (primeira chamada)
            assert call_count[0] == first_call_count  # Não aumentou na segunda chamada

    @pytest.mark.asyncio
    async def test_empty_file_paths_returns_empty_list(self):
        """Testa que lista vazia retorna lista vazia."""
        result = await get_signed_urls([])
        assert result == []

    @pytest.mark.asyncio
    async def test_partial_cache_hit(self):
        """Testa cache parcial - alguns arquivos no cache, outros não."""
        with patch("acesso_livre_api.storage.get_url.supabase_client") as mock_client:
            mock_storage = MagicMock()
            def mock_create_signed_url(path, expires):
                return {"signedURL": f"https://url-{path.split('.')[0]}.com"}
            
            mock_storage.create_signed_url.side_effect = mock_create_signed_url
            mock_client.return_value.storage.from_.return_value = mock_storage

            # Primeira chamada com 2 arquivos
            await get_signed_urls(["a.jpg", "b.jpg"])
            
            # Segunda chamada com 3 arquivos (2 cached, 1 novo)

            results = await get_signed_urls(["a.jpg", "b.jpg", "c.jpg"])

            assert len(results) == 3
            assert results[0] == "https://url-a.com"  # do cache
            assert results[1] == "https://url-b.com"  # do cache
            assert results[2] == "https://url-c.com"  # nova chamada
