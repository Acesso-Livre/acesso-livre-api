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
        "images": []
    }
    response = await client.post("/api/comments/", json=comment_data)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"

@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_comment_invalid_rating(client: AsyncClient, created_location):
    comment_data = {
        "user_name": "Test User",
        "rating": 6,
        "comment": "Invalid rating.",
        "location_id": created_location["id"]
    }
    response = await client.post("/api/comments/", json=comment_data)
    assert response.status_code == 422

@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_comment_nonexistent_location(client: AsyncClient):
    comment_data = {
        "user_name": "Test User",
        "rating": 5,
        "comment": "Location does not exist.",
        "location_id": 9999
    }
    response = await client.post("/api/comments/", json=comment_data)
    assert response.status_code == 500

@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_comments_by_location_id_success(client: AsyncClient, created_location, admin_auth_header):
    comment_data = {
        "user_name": "Commenter",
        "rating": 4,
        "comment": "A comment to be listed.",
        "location_id": created_location["id"],
        "images": []
    }
    create_response = await client.post("/api/comments/", json=comment_data)
    comment_id = create_response.json()["id"]
    
    # Approve the comment so it appears in the public endpoint
    await client.patch(f"/api/comments/{comment_id}/status", json={"status": "approved"}, headers=admin_auth_header)

    response = await client.get(f"/api/comments/{created_location['id']}/comments", headers=admin_auth_header)
    
    assert response.status_code == 200
    data = response.json()
    assert "comments" in data
    assert len(data["comments"]) > 0
    assert data["comments"][0]["user_name"] == "Commenter"
    assert data["comments"][0]["comment"] == "A comment to be listed."
    assert data["comments"][0]["location_id"] == created_location["id"]

@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_comments_by_location_id_no_comments(client: AsyncClient, created_location, admin_auth_header):
    response = await client.get(f"/api/comments/{created_location['id']}/comments", headers=admin_auth_header)
    
    assert response.status_code == 200
    data = response.json()
    assert "comments" in data
    assert len(data["comments"]) == 0

@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_comments_by_location_id_no_auth(client: AsyncClient, created_location):
    response = await client.get(f"/api/comments/{created_location['id']}/comments")
    assert response.status_code == 200
    data = response.json()
    assert "comments" in data

@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_pending_comments_success(client: AsyncClient, created_location, admin_auth_header):
    comment_data = {
        "user_name": "Pending User",
        "rating": 5,
        "comment": "This comment should be pending.",
        "location_id": created_location["id"],
        "images": []
    }
    await client.post("/api/comments/", json=comment_data)

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
async def test_update_comment_status_to_approved_success(client: AsyncClient, created_location, admin_auth_header):
    comment_data = {
        "user_name": "Status User", "rating": 3, "comment": "To be approved.", "location_id": created_location["id"]
    }
    create_response = await client.post("/api/comments/", json=comment_data)
    comment_id = create_response.json()["id"]

    update_data = {"status": "approved"}
    response = await client.patch(f"/api/comments/{comment_id}/status", json=update_data, headers=admin_auth_header)

    assert response.status_code == 200

@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_comment_status_not_pending(client: AsyncClient, created_location, admin_auth_header):
    comment_data = { "user_name": "Already Approved", "rating": 5, "comment": "Can't change status.", "location_id": created_location["id"] }
    create_response = await client.post("/api/comments/", json=comment_data)
    comment_id = create_response.json()["id"]
    await client.patch(f"/api/comments/{comment_id}/status", json={"status": "approved"}, headers=admin_auth_header)

    update_data = {"status": "rejected"}
    response = await client.patch(f"/api/comments/{comment_id}/status", json=update_data, headers=admin_auth_header)

    assert response.status_code == 422

@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_comment_status_not_found(client: AsyncClient, admin_auth_header):
    update_data = {"status": "approved"}
    response = await client.patch("/api/comments/9999/status", json=update_data, headers=admin_auth_header)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Comentário não encontrado"

@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_comment_status_no_auth(client: AsyncClient, created_location):
    comment_data = { "user_name": "No Auth Update", "rating": 4, "comment": "...", "location_id": created_location["id"] }
    create_response = await client.post("/api/comments/", json=comment_data)
    comment_id = create_response.json()["id"]

    update_data = {"status": "approved"}
    response = await client.patch(f"/api/comments/{comment_id}/status", json=update_data)
    
    assert response.status_code == 401

@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_comment_success(client: AsyncClient, created_location, admin_auth_header):
    comment_data = {
        "user_name": "To Be Deleted", "rating": 1, "comment": "Delete me.", "location_id": created_location["id"]
    }
    create_response = await client.post("/api/comments/", json=comment_data)
    comment_id = create_response.json()["id"]

    response = await client.delete(f"/api/comments/{comment_id}", headers=admin_auth_header)
    
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
    comment_data = { "user_name": "No Auth Delete", "rating": 2, "comment": "...", "location_id": created_location["id"] }
    create_response = await client.post("/api/comments/", json=comment_data)
    comment_id = create_response.json()["id"]

    response = await client.delete(f"/api/comments/{comment_id}")
    
    assert response.status_code == 401

@pytest.mark.asyncio
@pytest.mark.integration
async def test_read_comment_success(client: AsyncClient, created_location, admin_auth_header):
    comment_data = {
        "user_name": "Reader", "rating": 5, "comment": "Read me.", "location_id": created_location["id"]
    }
    create_response = await client.post("/api/comments/", json=comment_data)
    comment_id = create_response.json()["id"]
    
    # Approve the comment so it can be read from the public endpoint
    await client.patch(f"/api/comments/{comment_id}/status", json={"status": "approved"}, headers=admin_auth_header)

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
        "location_id": 9999
    }
    response = await client.post("/api/comments/", json=comment_data)
    assert response.status_code == 500

@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_comment_status_generic_exception(client: AsyncClient, created_location, admin_auth_header):
    """Testa o tratamento genérico de exceções no update_comment_status."""
    comment_data = {
        "user_name": "Test User", "rating": 5, "comment": "Test", "location_id": created_location["id"]
    }
    create_response = await client.post("/api/comments/", json=comment_data)
    comment_id = create_response.json()["id"]

    # Forçar uma situação que cause erro genérico (por exemplo, status inválido)
    update_data = {"status": "invalid_status"}
    response = await client.patch(f"/api/comments/{comment_id}/status", json=update_data, headers=admin_auth_header)
    assert response.status_code == 422

@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_comment_generic_exception(client: AsyncClient, created_location, admin_auth_header):
    """Testa o tratamento genérico de exceções no delete_comment."""
    comment_data = {
        "user_name": "Test User", "rating": 5, "comment": "Test", "location_id": created_location["id"]
    }
    create_response = await client.post("/api/comments/", json=comment_data)
    comment_id = create_response.json()["id"]

    # Deletar uma vez
    response = await client.delete(f"/api/comments/{comment_id}", headers=admin_auth_header)
    assert response.status_code == 200

    # Tentar deletar novamente (deve causar erro genérico)
    response = await client.delete(f"/api/comments/{comment_id}", headers=admin_auth_header)
    assert response.status_code == 404

@pytest.mark.asyncio
@pytest.mark.integration
async def test_read_comment_generic_exception(client: AsyncClient):
    """Testa o tratamento genérico de exceções no read_comment."""
    response = await client.get("/api/comments/9999")
    assert response.status_code == 404