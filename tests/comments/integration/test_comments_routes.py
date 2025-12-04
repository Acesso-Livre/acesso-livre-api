import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_comment_success(client: AsyncClient, created_location):
    comment_data = {
        "user_name": "Test User",
        "rating": 5,
        "comment": "This is a test comment.",
        "location_id": created_location["id"],
    }
    response = await client.post("/api/comments/", data=comment_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_comment_with_accessibility_items(
    client: AsyncClient, created_location, admin_auth_header
):
    # Primeiro criar um item de acessibilidade
    from io import BytesIO

    fake_image = BytesIO(b"fake image content")
    fake_image.name = "test_icon.png"

    item_response = await client.post(
        "/api/locations/accessibility-items/",
        data={"name": "Bebedouro Teste"},
        files={"image": ("test_icon.png", fake_image, "image/png")},
        headers=admin_auth_header,
    )

    if item_response.status_code == 200:
        item_id = item_response.json()["id"]

        # Criar comentário com accessibility_item_ids
        comment_data = {
            "user_name": "Test User",
            "rating": 5,
            "comment": "Local com bebedouro acessível.",
            "location_id": created_location["id"],
            "accessibility_item_ids": str(item_id),
        }
        response = await client.post("/api/comments/", data=comment_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"

        # Verificar se o item foi associado ao local
        location_response = await client.get(
            f"/api/comments/{created_location['id']}/comments"
        )
        assert location_response.status_code == 200
        location_data = location_response.json()
        assert "accessibility_items" in location_data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_comment_invalid_rating(client: AsyncClient, created_location):
    comment_data = {
        "user_name": "Test User",
        "rating": 6,
        "comment": "Invalid rating.",
        "location_id": created_location["id"],
    }
    response = await client.post("/api/comments/", data=comment_data)
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_comment_nonexistent_location(client: AsyncClient):
    comment_data = {
        "user_name": "Test User",
        "rating": 5,
        "comment": "Location does not exist.",
        "location_id": 9999,
    }
    response = await client.post("/api/comments/", data=comment_data)
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_comments_by_location_id_success(
    client: AsyncClient, created_location, admin_auth_header
):
    comment_data = {
        "user_name": "Commenter",
        "rating": 4,
        "comment": "A comment to be listed.",
        "location_id": created_location["id"],
        "images": [],
    }
    create_response = await client.post("/api/comments/", data=comment_data)
    comment_id = create_response.json()["id"]

    await client.patch(
        f"/api/comments/{comment_id}/status",
        json={"status": "approved"},
        headers=admin_auth_header,
    )

    response = await client.get(f"/api/comments/{created_location['id']}/comments")

    assert response.status_code == 200
    data = response.json()
    assert "comments" in data
    assert "accessibility_items" in data
    assert len(data["comments"]) == 1
    assert data["comments"][0]["id"] == comment_id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_comments_by_location_id_no_comments(
    client: AsyncClient, created_location, admin_auth_header
):
    response = await client.get(
        f"/api/comments/{created_location['id']}/comments", headers=admin_auth_header
    )

    assert response.status_code == 200
    data = response.json()
    assert "comments" in data
    assert "accessibility_items" in data
    assert len(data["comments"]) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_comments_by_location_id_no_auth(
    client: AsyncClient, created_location
):
    response = await client.get(f"/api/comments/{created_location['id']}/comments")
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_pending_comments_success(
    client: AsyncClient, created_location, admin_auth_header
):
    comment_data = {
        "user_name": "Pending User",
        "rating": 5,
        "comment": "This comment should be pending.",
        "location_id": created_location["id"],
        "images": [],
    }
    await client.post("/api/comments/", data=comment_data)

    response = await client.get("/api/comments/pending", headers=admin_auth_header)

    assert response.status_code == 200
    data = response.json()
    assert "comments" in data
    assert len(data["comments"]) > 0
    assert data["comments"][0]["status"] == "pending"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_pending_comments_no_pending(client: AsyncClient, admin_auth_header):
    response = await client.get("/api/comments/pending", headers=admin_auth_header)

    assert response.status_code == 200
    data = response.json()
    assert "comments" in data
    assert len(data["comments"]) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_pending_comments_no_auth(client: AsyncClient):
    response = await client.get("/api/comments/pending")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_comment_status_to_approved_success(
    client: AsyncClient, created_location, admin_auth_header
):
    comment_data = {
        "user_name": "Status User",
        "rating": 3,
        "comment": "To be approved.",
        "location_id": created_location["id"],
    }
    create_response = await client.post("/api/comments/", data=comment_data)
    comment_id = create_response.json()["id"]

    update_data = {"status": "approved"}
    response = await client.patch(
        f"/api/comments/{comment_id}/status", json=update_data, headers=admin_auth_header
    )

    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_comment_status_not_pending(
    client: AsyncClient, created_location, admin_auth_header
):
    comment_data = {
        "user_name": "Already Approved",
        "rating": 5,
        "comment": "Can't change status.",
        "location_id": created_location["id"],
    }
    create_response = await client.post("/api/comments/", data=comment_data)
    comment_id = create_response.json()["id"]
    await client.patch(
        f"/api/comments/{comment_id}/status",
        json={"status": "approved"},
        headers=admin_auth_header,
    )

    update_data = {"status": "rejected"}
    response = await client.patch(
        f"/api/comments/{comment_id}/status", json=update_data, headers=admin_auth_header
    )

    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_comment_status_not_found(client: AsyncClient, admin_auth_header):
    update_data = {"status": "approved"}
    response = await client.patch(
        "/api/comments/9999/status", json=update_data, headers=admin_auth_header
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Comentário não encontrado"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_comment_status_no_auth(client: AsyncClient, created_location):
    comment_data = {
        "user_name": "No Auth Update",
        "rating": 4,
        "comment": "...",
        "location_id": created_location["id"],
    }
    create_response = await client.post("/api/comments/", data=comment_data)
    comment_id = create_response.json()["id"]

    update_data = {"status": "approved"}
    response = await client.patch(f"/api/comments/{comment_id}/status", json=update_data)

    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_comment_success(
    client: AsyncClient, created_location, admin_auth_header
):
    comment_data = {
        "user_name": "To Be Deleted",
        "rating": 1,
        "comment": "Delete me.",
        "location_id": created_location["id"],
    }
    create_response = await client.post("/api/comments/", data=comment_data)
    comment_id = create_response.json()["id"]

    response = await client.delete(
        f"/api/comments/{comment_id}", headers=admin_auth_header
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Comment deleted successfully"

    get_response = await client.get(f"/api/comments/{comment_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_comment_not_found(client: AsyncClient, admin_auth_header):
    response = await client.delete("/api/comments/9999", headers=admin_auth_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "Comentário não encontrado"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_comment_no_auth(client: AsyncClient, created_location):
    comment_data = {
        "user_name": "No Auth Delete",
        "rating": 2,
        "comment": "...",
        "location_id": created_location["id"],
    }
    create_response = await client.post("/api/comments/", data=comment_data)
    comment_id = create_response.json()["id"]

    response = await client.delete(f"/api/comments/{comment_id}")

    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
async def test_read_comment_success(
    client: AsyncClient, created_location, admin_auth_header
):
    comment_data = {
        "user_name": "Reader",
        "rating": 5,
        "comment": "Read me.",
        "location_id": created_location["id"],
    }
    create_response = await client.post("/api/comments/", data=comment_data)
    comment_id = create_response.json()["id"]

    await client.patch(
        f"/api/comments/{comment_id}/status",
        json={"status": "approved"},
        headers=admin_auth_header,
    )

    response = await client.get(f"/api/comments/{comment_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == comment_id
    assert data["user_name"] == "Reader"
    assert data["comment"] == "Read me."


@pytest.mark.asyncio
@pytest.mark.integration
async def test_read_comment_not_found(client: AsyncClient):
    response = await client.get("/api/comments/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Comentário não encontrado"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_comment_location_not_found_exception(client: AsyncClient):
    """Testa o tratamento específico da LocationNotFoundException no router."""
    comment_data = {
        "user_name": "Test User",
        "rating": 5,
        "comment": "This should trigger LocationNotFoundException",
        "location_id": 9999,
    }
    response = await client.post("/api/comments/", data=comment_data)
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_comment_status_generic_exception(
    client: AsyncClient, created_location, admin_auth_header
):
    """Testa o tratamento genérico de exceções no update_comment_status."""
    comment_data = {
        "user_name": "Test User",
        "rating": 5,
        "comment": "Test",
        "location_id": created_location["id"],
    }
    create_response = await client.post("/api/comments/", data=comment_data)
    comment_id = create_response.json()["id"]

    # Forçar uma situação que cause erro genérico (por exemplo, status inválido)
    update_data = {"status": "invalid_status"}
    response = await client.patch(
        f"/api/comments/{comment_id}/status", json=update_data, headers=admin_auth_header
    )
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_comment_twice_returns_404(
    client: AsyncClient, created_location, admin_auth_header
):
    """Testa que deletar um comentário já deletado retorna 404."""
    comment_data = {
        "user_name": "Test User",
        "rating": 5,
        "comment": "Test",
        "location_id": created_location["id"],
    }
    create_response = await client.post("/api/comments/", data=comment_data)
    comment_id = create_response.json()["id"]

    # Deletar uma vez
    response = await client.delete(
        f"/api/comments/{comment_id}", headers=admin_auth_header
    )
    assert response.status_code == 200

    # Tentar deletar novamente deve retornar 404 pois não existe mais
    response = await client.delete(
        f"/api/comments/{comment_id}", headers=admin_auth_header
    )
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_read_comment_generic_exception(client: AsyncClient):
    """Testa o tratamento genérico de exceções no read_comment."""
    response = await client.get("/api/comments/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_read_pending_comment_fails(client: AsyncClient, created_location):
    """Testa que um comentário pendente não pode ser lido pelo endpoint de detalhe."""
    comment_data = {
        "user_name": "Ghost User",
        "rating": 4,
        "comment": "This comment is pending and should not be visible.",
        "location_id": created_location["id"],
    }
    create_response = await client.post("/api/comments/", data=comment_data)
    comment_id = create_response.json()["id"]

    response = await client.get(f"/api/comments/{comment_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_recent_comments_success(
    client: AsyncClient, created_location, admin_auth_header
):
    # Create 5 comments
    for i in range(5):
        comment_data = {
            "user_name": f"User {i}",
            "rating": 5 - i,
            "comment": f"Test comment {i}",
            "location_id": created_location["id"],
        }
        create_response = await client.post("/api/comments/", data=comment_data)
        comment_id = create_response.json()["id"]

        # Approve the comment
        update_data = {"status": "approved"}
        await client.patch(
            f"/api/comments/{comment_id}/status",
            json=update_data,
            headers=admin_auth_header,
        )

    # Get recent comments (should return last 3)
    response = await client.get("/api/comments/recent")
    assert response.status_code == 200

    data = response.json()
    assert "comments" in data
    assert len(data["comments"]) == 3

    # Verify structure of each comment
    for comment in data["comments"]:
        assert "location_name" in comment
        assert "location_rating" in comment
        assert "user_name" in comment
        assert "description" in comment
        assert isinstance(comment["location_name"], str)
        assert isinstance(comment["location_rating"], (int, float))
        assert isinstance(comment["user_name"], str)
        assert isinstance(comment["description"], str)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_recent_comments_with_custom_limit(
    client: AsyncClient, created_location, admin_auth_header
):
    # Create 5 comments
    for i in range(5):
        comment_data = {
            "user_name": f"User {i}",
            "rating": 5,
            "comment": f"Test comment {i}",
            "location_id": created_location["id"],
        }
        create_response = await client.post("/api/comments/", data=comment_data)
        comment_id = create_response.json()["id"]

        # Approve the comment
        update_data = {"status": "approved"}
        await client.patch(
            f"/api/comments/{comment_id}/status",
            json=update_data,
            headers=admin_auth_header,
        )

    # Get recent comments with limit=5
    response = await client.get("/api/comments/recent?limit=5")
    assert response.status_code == 200

    data = response.json()
    assert len(data["comments"]) == 5


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_recent_comments_empty(client: AsyncClient):
    # Get recent comments when none exist
    response = await client.get("/api/comments/recent")
    assert response.status_code == 200

    data = response.json()
    assert data["comments"] == []


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_recent_comments_only_approved(
    client: AsyncClient, created_location, admin_auth_header
):
    # Create one approved comment
    comment_data = {
        "user_name": "Approved User",
        "rating": 5,
        "comment": "This is approved.",
        "location_id": created_location["id"],
    }
    create_response = await client.post("/api/comments/", data=comment_data)
    approved_comment_id = create_response.json()["id"]

    update_data = {"status": "approved"}
    await client.patch(
        f"/api/comments/{approved_comment_id}/status",
        json=update_data,
        headers=admin_auth_header,
    )

    # Create one pending comment (should not appear in recent)
    comment_data = {
        "user_name": "Pending User",
        "rating": 4,
        "comment": "This is pending.",
        "location_id": created_location["id"],
    }
    await client.post("/api/comments/", data=comment_data)

    # Get recent comments
    response = await client.get("/api/comments/recent")
    assert response.status_code == 200

    data = response.json()
    assert len(data["comments"]) == 1
    assert data["comments"][0]["user_name"] == "Approved User"
