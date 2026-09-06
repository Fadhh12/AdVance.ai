"""Template gallery (Phase 6R): the SQLite-in-memory test DB doesn't run Alembic
migrations (see conftest.py), so seed data is inserted directly per test rather than
relying on the migration's `op.bulk_insert` seed rows.
"""
import app.models.base as models_base
from app.models.template import Template


def _auth_headers(client, email="templates@example.com") -> dict:
    response = client.post(
        "/auth/register", json={"email": email, "password": "hunter22", "name": "Nabil"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _seed_templates():
    db = models_base.SessionLocal()
    try:
        db.add_all(
            [
                Template(
                    name="Unboxing Produk",
                    description="Gaya unboxing.",
                    mode="product_ad",
                    prompt_preset="gaya unboxing, close-up",
                    is_active=True,
                ),
                Template(
                    name="Testimoni Pelanggan",
                    description="Gaya testimoni.",
                    mode="affiliate",
                    prompt_preset="gaya testimoni to-camera",
                    is_active=True,
                ),
                Template(
                    name="Draf Lama",
                    description="Tidak dipakai lagi.",
                    mode="product_ad",
                    prompt_preset="tidak dipakai",
                    is_active=False,
                ),
            ]
        )
        db.commit()
    finally:
        db.close()


def test_list_templates_returns_only_active(client):
    headers = _auth_headers(client)
    _seed_templates()

    response = client.get("/templates", headers=headers)
    assert response.status_code == 200
    names = {t["name"] for t in response.json()}
    assert names == {"Unboxing Produk", "Testimoni Pelanggan"}


def test_list_templates_filters_by_mode(client):
    headers = _auth_headers(client)
    _seed_templates()

    response = client.get("/templates", params={"mode": "affiliate"}, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Testimoni Pelanggan"


def test_list_templates_requires_auth(client):
    _seed_templates()
    response = client.get("/templates")
    assert response.status_code == 401
