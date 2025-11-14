import pytest


@pytest.mark.auth
class TestAuthentication:
    """Test authentication endpoints"""

    def test_register_user(self, client):
        """Test user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "full_name": "New User",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "newuser"
        assert data["user"]["email"] == "newuser@example.com"

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",  # Already exists
                "email": "different@example.com",
                "full_name": "Different User",
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "differentuser",
                "email": "test@example.com",  # Already exists
                "full_name": "Different User",
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 401

    def test_get_current_user(self, client, auth_headers, test_user):
        """Test getting current user info"""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403  # No authorization header

    def test_forgot_password(self, client, test_user):
        """Test password reset request"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "reset_code" in data
        assert len(data["reset_code"]) == 9  # Code length

    def test_forgot_password_nonexistent_email(self, client):
        """Test password reset for non-existent email"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )
        # Should return 200 for security (don't reveal if email exists)
        assert response.status_code == 200
        assert "reset_code" in response.json()

    def test_reset_password(self, client, test_user, db_session):
        """Test password reset with valid code"""
        # First, request reset code
        reset_response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@example.com"}
        )
        reset_code = reset_response.json()["reset_code"]

        # Now reset password
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "email": "test@example.com",
                "reset_code": reset_code,
                "new_password": "newpassword123"
            }
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Test login with new password
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "newpassword123"
            }
        )
        assert login_response.status_code == 200

    def test_reset_password_invalid_code(self, client, test_user):
        """Test password reset with invalid code"""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "email": "test@example.com",
                "reset_code": "INVALIDCODE",
                "new_password": "newpassword123"
            }
        )
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    def test_logout(self, client):
        """Test logout endpoint"""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        assert response.json()["success"] is True
