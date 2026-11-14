"""Roles, the admin guard, and manual B2 backups / restores (B2 is faked)."""

import gzip
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from testing.fakes import FakeUpstream, b2_file_id, movie_add_payload

ADMIN_ROUTES = [
    ("POST", "/api/admin/backup", None),
    ("GET", "/api/admin/backups", None),
    ("POST", "/api/admin/restore", {"name": "manual-backups/x.db.gz"}),
]


def test_role_is_reported_on_me(alice: TestClient, admin: TestClient) -> None:
    assert alice.get("/api/auth/me").json()["role"] == "user"
    assert admin.get("/api/auth/me").json()["role"] == "admin"


@pytest.mark.parametrize(("method", "url", "body"), ADMIN_ROUTES)
def test_admin_routes_reject_regular_users(
    alice: TestClient, upstream: FakeUpstream, method: str, url: str, body: dict[str, str] | None
) -> None:
    response = alice.request(method, url, json=body)

    assert response.status_code == 403
    assert upstream.b2_files == {}


@pytest.mark.parametrize(("method", "url", "body"), ADMIN_ROUTES)
def test_admin_routes_require_login(
    client: TestClient, method: str, url: str, body: dict[str, str] | None
) -> None:
    assert client.request(method, url, json=body).status_code == 401


def test_backup_uploads_a_gzipped_sqlite_snapshot(
    admin: TestClient, upstream: FakeUpstream, tmp_path: Path
) -> None:
    response = admin.post("/api/admin/backup")

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"].startswith("manual-backups/beantrack-")
    assert body["name"].endswith(".db.gz")
    data, _ = upstream.b2_files[body["name"]]
    assert body["size"] == len(data)

    snapshot = tmp_path / "check.db"
    snapshot.write_bytes(gzip.decompress(data))
    with sqlite3.connect(snapshot) as conn:
        users = conn.execute("SELECT username, role FROM users").fetchall()
    assert ("root", "admin") in users


def test_list_backups_newest_first(admin: TestClient) -> None:
    first = admin.post("/api/admin/backup").json()["name"]
    second = admin.post("/api/admin/backup").json()["name"]

    backups = admin.get("/api/admin/backups").json()

    assert [b["name"] for b in backups] == [second, first]
    assert all(b["size"] > 0 and b["created_at"] for b in backups)


def test_restore_brings_back_the_snapshot_and_keeps_a_safety_copy(
    admin: TestClient, alice: TestClient, upstream: FakeUpstream
) -> None:
    alice.post("/api/movielist/add", json=movie_add_payload())
    backup = admin.post("/api/admin/backup").json()["name"]
    alice.delete("/api/movielist/tt0133093")
    assert alice.get("/api/movielist").json()["entries"] == []

    response = admin.post("/api/admin/restore", json={"name": backup})

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["restored"]["name"] == backup
    assert body["safety_backup"]["name"].endswith("-pre-restore.db.gz")
    assert body["safety_backup"]["name"] in upstream.b2_files
    entries = alice.get("/api/movielist").json()["entries"]
    assert [e["movie"]["imdb"] for e in entries] == ["tt0133093"]


def test_restore_rejects_unknown_or_foreign_names(admin: TestClient) -> None:
    assert (
        admin.post("/api/admin/restore", json={"name": "../etc/passwd"}).status_code == 422
    )
    assert (
        admin.post(
            "/api/admin/restore", json={"name": "manual-backups/missing.db.gz"}
        ).status_code
        == 422
    )


def test_restore_rejects_a_corrupt_backup(admin: TestClient, upstream: FakeUpstream) -> None:
    upstream.b2_files["manual-backups/broken.db.gz"] = (gzip.compress(b"not sqlite"), 1)

    response = admin.post("/api/admin/restore", json={"name": "manual-backups/broken.db.gz"})

    assert response.status_code == 422


def test_backups_have_ids_and_can_be_deleted(admin: TestClient, upstream: FakeUpstream) -> None:
    keep = admin.post("/api/admin/backup").json()
    gone = admin.post("/api/admin/backup").json()

    response = admin.delete(f"/api/admin/backups/{gone['id']}")

    assert response.status_code == 204
    assert [b["id"] for b in admin.get("/api/admin/backups").json()] == [keep["id"]]
    assert gone["name"] not in upstream.b2_files


def test_delete_only_reaches_manual_backups(admin: TestClient, upstream: FakeUpstream) -> None:
    litestream_file = "beantrack/generations/0/snapshot.ltx"
    upstream.b2_files[litestream_file] = (b"litestream", 1)

    response = admin.delete(f"/api/admin/backups/{b2_file_id(litestream_file)}")

    assert response.status_code == 404
    assert litestream_file in upstream.b2_files


def test_delete_backup_is_admin_only(alice: TestClient, client: TestClient) -> None:
    assert alice.delete("/api/admin/backups/whatever").status_code == 403
    assert client.delete("/api/admin/backups/whatever").status_code == 401
