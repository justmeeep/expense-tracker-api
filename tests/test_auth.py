def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"email": "a@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "a@example.com"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email(client):
    payload = {"email": "a@example.com", "password": "password123"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409


def test_register_short_password(client):
    response = client.post(
        "/auth/register",
        json={"email": "a@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"email": "a@example.com", "password": "password123"},
    )
    response = client.post(
        "/auth/login",
        data={"username": "a@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={"email": "a@example.com", "password": "password123"},
    )
    response = client.post(
        "/auth/login",
        data={"username": "a@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_me_requires_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_token(client, make_user):
    headers = make_user("a@example.com")
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "a@example.com"
