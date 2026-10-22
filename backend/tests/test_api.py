import pytest
from httpx import AsyncClient
from backend.app.main import app


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "tensor-hub-ryan-vo"


class TestIssuesAPI:
    @pytest.mark.asyncio
    async def test_create_issue(self, client):
        issue_data = {
            "title": "Test segfault",
            "body": "Segmentation fault in ZEND_NEW_SPEC_CONST_UNUSED_HANDLER with CACHED_PTR",
            "php_version": "8.1.1",
            "os": "CentOS 7",
        }
        response = await client.post("/api/issues", json=issue_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == issue_data["title"]
        assert data["category"] == "segfault"
        assert data["status"] in ["analyzed", "test_generated"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_analyze_endpoint(self, client):
        request_data = {
            "title": "Test performance issue",
            "body": "GC_THRESHOLD causing slowdown in phpunit tests",
            "php_version": "8.1.12",
            "os": "Docker",
        }
        response = await client.post("/api/issues/analyze", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "issue" in data
        assert "analysis" in data
        assert data["analysis"]["classification"] == "performance"
        assert "test_case" in data
        assert data["test_case"] is not None

    @pytest.mark.asyncio
    async def test_list_issues(self, client):
        # Create a few issues first
        for i in range(3):
            await client.post("/api/issues", json={
                "title": f"Issue {i}",
                "body": "Test body",
            })

        response = await client.get("/api/issues")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        assert len(data["items"]) >= 3
        assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_list_issues_with_filter(self, client):
        await client.post("/api/issues", json={
            "title": "Segfault test",
            "body": "Segmentation fault in ZEND_NEW_SPEC_CONST_UNUSED_HANDLER",
        })

        response = await client.get("/api/issues?category=segfault")
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["category"] == "segfault"

    @pytest.mark.asyncio
    async def test_get_issue(self, client):
        create_resp = await client.post("/api/issues", json={
            "title": "Get test",
            "body": "Test body",
        })
        issue_id = create_resp.json()["id"]

        response = await client.get(f"/api/issues/{issue_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == issue_id
        assert data["title"] == "Get test"

    @pytest.mark.asyncio
    async def test_get_nonexistent_issue(self, client):
        response = await client.get("/api/issues/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_issue(self, client):
        create_resp = await client.post("/api/issues", json={
            "title": "Original title",
            "body": "Test body",
        })
        issue_id = create_resp.json()["id"]

        response = await client.patch(f"/api/issues/{issue_id}", json={
            "title": "Updated title",
            "status": "closed",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["status"] == "closed"

    @pytest.mark.asyncio
    async def test_delete_issue(self, client):
        create_resp = await client.post("/api/issues", json={
            "title": "To delete",
            "body": "Test body",
        })
        issue_id = create_resp.json()["id"]

        response = await client.delete(f"/api/issues/{issue_id}")
        assert response.status_code == 204

        get_resp = await client.get(f"/api/issues/{issue_id}")
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_reanalyze_issue(self, client):
        create_resp = await client.post("/api/issues", json={
            "title": "Reanalyze test",
            "body": "Segmentation fault in ZEND_NEW_SPEC_CONST_UNUSED_HANDLER",
        })
        issue_id = create_resp.json()["id"]

        response = await client.post(f"/api/issues/{issue_id}/reanalyze")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == issue_id