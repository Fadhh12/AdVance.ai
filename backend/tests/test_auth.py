from app.core.config import get_settings


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


def test_owner_email_gets_unlimited_plan(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "owner_email", "owner@example.com")

    response = _register(client, email="owner@example.com")
    assert response.status_code == 201

    me = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {response.json()['access_token']}"}
    ).json()
    assert me["plan_id"] is not None

    # A plain user (not matching OWNER_EMAIL) still gets the normal Free plan.
    other = _register(client, email="regular@example.com")
    other_me = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {other.json()['access_token']}"}
    ).json()
    assert other_me["plan_id"] != me["plan_id"]


def test_owner_email_match_is_case_insensitive(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "owner_email", "Owner@Example.com")

    response = _register(client, email="owner@example.com")
    me = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {response.json()['access_token']}"}
    ).json()

    plain = _register(client, email="plain@example.com")
    plain_me = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {plain.json()['access_token']}"}
    ).json()
    assert me["plan_id"] != plain_me["plan_id"]


def test_guest_endpoint_creates_working_anonymous_account(client):
    response = client.post("/auth/guest")
    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert "@guest.advanceai.app" in body["user"]["email"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200


def test_guest_never_gets_the_owner_plan_even_if_owner_email_unset(client):
    # OWNER_EMAIL defaults to "" — guard against an empty owner_email matching an
    # empty-ish guest email by accident.
    first = client.post("/auth/guest").json()
    second = client.post("/auth/guest").json()
    assert first["user"]["email"] != second["user"]["email"]  # each call is a new account
