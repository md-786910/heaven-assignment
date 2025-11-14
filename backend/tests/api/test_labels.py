import pytest


@pytest.mark.labels
class TestLabels:
    """Test label endpoints"""

    def test_create_label(self, client):
        """Test creating a label"""
        response = client.post(
            "/api/v1/labels",
            json={
                "name": "Bug",
                "color": "#FF0000"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Bug"
        assert data["color"] == "#FF0000"

    def test_create_duplicate_label(self, client, test_label):
        """Test creating duplicate label"""
        response = client.post(
            "/api/v1/labels",
            json={
                "name": test_label["name"],
                "color": "#00FF00"
            }
        )
        assert response.status_code == 400

    def test_get_all_labels(self, client, test_label):
        """Test getting all labels"""
        response = client.get("/api/v1/labels")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_assign_labels_to_issue(self, client, test_issue, test_label):
        """Test assigning labels to an issue"""
        response = client.put(
            f"/api/v1/labels/issues/{test_issue['id']}/labels",
            params={"label_ids": [test_label["id"]]}
        )
        assert response.status_code == 200

        # Verify labels are assigned
        issue_response = client.get(f"/api/v1/issues/{test_issue['id']}")
        assert len(issue_response.json()["labels"]) == 1
        assert issue_response.json()["labels"][0]["id"] == test_label["id"]

    def test_replace_labels(self, client, test_issue, test_label):
        """Test replacing labels (atomic operation)"""
        # First assign a label
        client.put(
            f"/api/v1/labels/issues/{test_issue['id']}/labels",
            params={"label_ids": [test_label["id"]]}
        )

        # Create another label
        label2_response = client.post(
            "/api/v1/labels",
            json={"name": "Enhancement", "color": "#00FF00"}
        )
        label2 = label2_response.json()

        # Replace with new label
        response = client.put(
            f"/api/v1/labels/issues/{test_issue['id']}/labels",
            params={"label_ids": [label2["id"]]}
        )
        assert response.status_code == 200

        # Verify only new label is present
        issue_response = client.get(f"/api/v1/issues/{test_issue['id']}")
        assert len(issue_response.json()["labels"]) == 1
        assert issue_response.json()["labels"][0]["id"] == label2["id"]

    def test_assign_nonexistent_label(self, client, test_issue):
        """Test assigning non-existent label"""
        response = client.put(
            f"/api/v1/labels/issues/{test_issue['id']}/labels",
            params={"label_ids": [99999]}
        )
        assert response.status_code == 404
