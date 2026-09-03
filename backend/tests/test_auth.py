def _register(client, email="creator@example.com", password="hunter22", name="Nabil"):
    return client.post(
        "/auth/register", json={"email": email, "password": password, "name": name}
    )


def test_register_returns_token_and_default_plan(client):
    response = _register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["user"]["email"] == "creator@example.com"
    assert body["user"]["ai_generation_used"] == 0
    # seeded "Free" plan from the first migration should be auto-assigned
    assert body["user"]["plan_id"] is not None


def test_register_duplicate_email_conflicts(client):
    _register(client)
    response = _register(client)
    assert response.status_code == 409


def test_login_with_correct_password_succeeds(client):
    _register(client, email="login@example.com", password="correcthorse")
    response = client.post(
        "/auth/login", json={"email": "login@example.com", "password": "correcthorse"}
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_with_wrong_password_fails(client):
    _register(client, email="wrong@example.com", password="correcthorse")
    response = client.post(
        "/auth/login", json={"email": "wrong@example.com", "password": "nope"}
    )
    assert response.status_code == 401


def test_me_requires_valid_token(client):
    register_response = _register(client, email="me@example.com")
    token = register_response.json()["access_token"]

    unauthorized = client.get("/auth/me")
    assert unauthorized.status_code == 401

    authorized = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert authorized.status_code == 200
    assert authorized.json()["email"] == "me@example.com"
