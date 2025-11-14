import pytest


@pytest.mark.issues
class TestIssues:
    """Test issue management endpoints"""

    def test_create_issue(self, client, auth_headers, test_user):
        """Test creating an issue"""
        response = client.post(
            "/api/v1/issues",
            headers=auth_headers,
            json={
                "title": "New Issue",
                "description": "Issue description",
                "status": "open",
                "priority": "high",
                "creator_id": test_user.id
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Issue"
        assert data["status"] == "open"
        assert data["priority"] == "high"
        assert data["version"] == 1

    def test_create_issue_without_auth(self, client, test_user):
        """Test creating issue without authentication"""
        response = client.post(
            "/api/v1/issues",
            json={
                "title": "New Issue",
                "description": "Issue description",
                "status": "open",
                "priority": "high",
                "creator_id": test_user.id
            }
        )
        assert response.status_code == 403

    def test_get_all_issues(self, client, test_issue):
        """Test getting all issues (public)"""
        response = client.get("/api/v1/issues")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_issue_by_id(self, client, test_issue):
        """Test getting a specific issue"""
        response = client.get(f"/api/v1/issues/{test_issue['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_issue["id"]
        assert data["title"] == test_issue["title"]
        assert "comments" in data
        assert "labels" in data

    def test_get_nonexistent_issue(self, client):
        """Test getting non-existent issue"""
        response = client.get("/api/v1/issues/99999")
        assert response.status_code == 404

    def test_update_issue(self, client, auth_headers, test_issue):
        """Test updating an issue"""
        response = client.patch(
            f"/api/v1/issues/{test_issue['id']}",
            headers=auth_headers,
            json={
                "title": "Updated Title",
                "status": "in_progress",
                "version": test_issue["version"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "in_progress"
        assert data["version"] == test_issue["version"] + 1

    def test_update_issue_version_mismatch(self, client, auth_headers, test_issue):
        """Test update with wrong version (optimistic locking)"""
        response = client.patch(
            f"/api/v1/issues/{test_issue['id']}",
            headers=auth_headers,
            json={
                "title": "Updated Title",
                "version": 999  # Wrong version
            }
        )
        assert response.status_code == 409
        assert "version" in response.json()["detail"].lower()

    def test_update_issue_without_auth(self, client, test_issue):
        """Test updating issue without authentication"""
        response = client.patch(
            f"/api/v1/issues/{test_issue['id']}",
            json={
                "title": "Updated Title",
                "version": test_issue["version"]
            }
        )
        assert response.status_code == 403

    def test_delete_issue(self, client, auth_headers, test_issue):
        """Test deleting an issue"""
        response = client.delete(
            f"/api/v1/issues/{test_issue['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Verify it's deleted
        get_response = client.get(f"/api/v1/issues/{test_issue['id']}")
        assert get_response.status_code == 404

    def test_delete_issue_without_auth(self, client, test_issue):
        """Test deleting issue without authentication"""
        response = client.delete(f"/api/v1/issues/{test_issue['id']}")
        assert response.status_code == 403

    def test_filter_issues_by_status(self, client, test_issue):
        """Test filtering issues by status"""
        response = client.get("/api/v1/issues?status=open")
        assert response.status_code == 200
        data = response.json()
        assert all(issue["status"] == "open" for issue in data)

    def test_bulk_status_update(self, client, auth_headers, test_issue):
        """Test bulk status update"""
        # Create another issue
        issue2 = client.post(
            "/api/v1/issues",
            headers=auth_headers,
            json={
                "title": "Issue 2",
                "description": "Description 2",
                "status": "open",
                "priority": "low",
                "creator_id": test_issue["creator_id"]
            }
        ).json()

        # Bulk update
        response = client.post(
            "/api/v1/issues/bulk-status",
            headers=auth_headers,
            json={
                "issue_ids": [test_issue["id"], issue2["id"]],
                "status": "resolved"
            }
        )
        assert response.status_code == 200

        # Verify updates
        for issue_id in [test_issue["id"], issue2["id"]]:
            check = client.get(f"/api/v1/issues/{issue_id}")
            assert check.json()["status"] == "resolved"

    def test_bulk_status_update_without_auth(self, client, test_issue):
        """Test bulk update without authentication"""
        response = client.post(
            "/api/v1/issues/bulk-status",
            json={
                "issue_ids": [test_issue["id"]],
                "status": "resolved"
            }
        )
        assert response.status_code == 403

    def test_get_issue_timeline(self, client, auth_headers, test_issue):
        """Test getting issue timeline"""
        # Make an update to create timeline entry
        client.patch(
            f"/api/v1/issues/{test_issue['id']}",
            headers=auth_headers,
            json={
                "status": "in_progress",
                "version": test_issue["version"]
            }
        )

        # Get timeline
        response = client.get(f"/api/v1/issues/{test_issue['id']}/timeline")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "field_name" in data[0]
        assert "old_value" in data[0]
        assert "new_value" in data[0]
