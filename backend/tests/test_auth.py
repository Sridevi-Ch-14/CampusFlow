def test_register_and_login(client):
    # 1. Register student
    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "teststudent@campusflow.edu",
            "full_name": "Test Student",
            "password": "Password123!",
            "role": "STUDENT"
        }
    )
    assert reg_response.status_code == 201
    data = reg_response.json()
    assert data["email"] == "teststudent@campusflow.edu"
    assert data["role"] == "STUDENT"

    # 2. Login with correct credentials
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "teststudent@campusflow.edu",
            "password": "Password123!"
        }
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # 3. Login with wrong password
    bad_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "teststudent@campusflow.edu",
            "password": "WrongPassword!"
        }
    )
    assert bad_login.status_code == 401
