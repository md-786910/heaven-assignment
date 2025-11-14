import pytest


@pytest.mark.reports
class TestReports:
    """Test report endpoints"""

    def test_top_assignees_report(self, client, auth_headers, test_user, test_user_2):
        """Test top assignees report"""
        # Create issues with different assignees
        for i in range(3):
            client.post(
                "/api/v1/issues",
                headers=auth_headers,
                json={
                    "title": f"Issue {i}",
                    "description": "Test",
                    "status": "open",
                    "priority": "medium",
                    "creator_id": test_user.id,
                    "assignee_id": test_user.id
                }
            )

        response = client.get("/api/v1/reports/top-assignees?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "assignee_id" in data[0]
        assert "issue_count" in data[0]
        assert "assignee_name" in data[0]

    def test_latency_report(self, client, auth_headers, test_user):
        """Test average resolution time report"""
        # Create and resolve an issue
        issue_response = client.post(
            "/api/v1/issues",
            headers=auth_headers,
            json={
                "title": "Resolved Issue",
                "description": "Test",
                "status": "open",
                "priority": "medium",
                "creator_id": test_user.id
            }
        )
        issue = issue_response.json()

        # Resolve it
        client.patch(
            f"/api/v1/issues/{issue['id']}",
            headers=auth_headers,
            json={
                "status": "resolved",
                "version": issue["version"]
            }
        )

        response = client.get("/api/v1/reports/latency")
        assert response.status_code == 200
        data = response.json()
        assert "average_resolution_time_hours" in data
        assert isinstance(data["average_resolution_time_hours"], (int, float)) or data["average_resolution_time_hours"] is None

    def test_empty_reports(self, client):
        """Test reports with no data"""
        response = client.get("/api/v1/reports/top-assignees")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        response = client.get("/api/v1/reports/latency")
        assert response.status_code == 200
