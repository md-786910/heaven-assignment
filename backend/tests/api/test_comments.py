import pytest


@pytest.mark.comments
class TestComments:
    """Test comment endpoints"""

    def test_add_comment(self, client, auth_headers, test_issue):
        """Test adding a comment to an issue"""
        response = client.post(
            f"/api/v1/issues/{test_issue['id']}/comments",
            headers=auth_headers,
            json={
                "body": "This is a test comment",
                "author_id": test_issue["creator_id"]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["body"] == "This is a test comment"
        assert data["issue_id"] == test_issue["id"]

    def test_add_comment_without_auth(self, client, test_issue, test_user):
        """Test adding comment without authentication"""
        response = client.post(
            f"/api/v1/issues/{test_issue['id']}/comments",
            json={
                "body": "This is a test comment",
                "author_id": test_user.id
            }
        )
        assert response.status_code == 403

    def test_add_comment_empty_body(self, client, auth_headers, test_issue, test_user):
        """Test adding comment with empty body"""
        response = client.post(
            f"/api/v1/issues/{test_issue['id']}/comments",
            headers=auth_headers,
            json={
                "body": "",
                "author_id": test_user.id
            }
        )
        assert response.status_code == 422  # Validation error

    def test_add_comment_nonexistent_issue(self, client, auth_headers, test_user):
        """Test adding comment to non-existent issue"""
        response = client.post(
            "/api/v1/issues/99999/comments",
            headers=auth_headers,
            json={
                "body": "This is a test comment",
                "author_id": test_user.id
            }
        )
        assert response.status_code == 404

    def test_comments_in_issue_details(self, client, auth_headers, test_issue):
        """Test that comments appear in issue details"""
        # Add a comment
        client.post(
            f"/api/v1/issues/{test_issue['id']}/comments",
            headers=auth_headers,
            json={
                "body": "Test comment",
                "author_id": test_issue["creator_id"]
            }
        )

        # Get issue details
        response = client.get(f"/api/v1/issues/{test_issue['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["comments"]) >= 1
        assert data["comments"][0]["body"] == "Test comment"
        assert "author" in data["comments"][0]
