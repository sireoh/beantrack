from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Movie
from testing.fakes import FakeUpstream


def test_get_movielist_starts_empty(alice: TestClient) -> None:
    response = alice.get("/api/movielist")

    assert response.status_code == 200
    assert response.json()["entries"] == []


def test_add_movie_returns_entry(alice: TestClient) -> None:
    response = alice.post("/api/movielist/add", json={"imdb": "tt0133093", "status": "completed"})

    assert response.status_code == 201, response.text
    entry = response.json()
    assert entry["status"] == "completed"
    assert entry["movie"] == {
        "imdb": "tt0133093",
        "title": "The Matrix",
        "image": "https://m.media-amazon.com/matrix.jpg",
        "score": 8.7,
    }


def test_add_movie_maps_omdb_na_to_null(alice: TestClient) -> None:
    entry = alice.post("/api/movielist/add", json={"imdb": "tt0816692"}).json()

    assert entry["movie"]["image"] is None
    assert entry["movie"]["score"] is None
    assert entry["status"] == "planned"


def test_get_movielist_returns_added_movies(alice: TestClient) -> None:
    alice.post("/api/movielist/add", json={"imdb": "tt0133093", "status": "watching"})
    alice.post("/api/movielist/add", json={"imdb": "tt0816692"})

    entries = alice.get("/api/movielist").json()["entries"]

    assert [(e["movie"]["imdb"], e["status"]) for e in entries] == [
        ("tt0133093", "watching"),
        ("tt0816692", "planned"),
    ]


def test_add_same_movie_twice_is_conflict(alice: TestClient) -> None:
    alice.post("/api/movielist/add", json={"imdb": "tt0133093"})

    assert alice.post("/api/movielist/add", json={"imdb": "tt0133093"}).status_code == 409


def test_delete_movie_removes_only_the_user_entry(alice: TestClient, bob: TestClient) -> None:
    alice.post("/api/movielist/add", json={"imdb": "tt0133093"})
    bob.post("/api/movielist/add", json={"imdb": "tt0133093"})

    response = alice.delete("/api/movielist/tt0133093")

    assert response.status_code == 204
    assert alice.get("/api/movielist").json()["entries"] == []
    assert len(bob.get("/api/movielist").json()["entries"]) == 1


def test_delete_missing_movie_is_404(alice: TestClient) -> None:
    response = alice.delete("/api/movielist/tt0133093")

    assert response.status_code == 404


def test_add_unknown_movie_is_404(alice: TestClient) -> None:
    assert alice.post("/api/movielist/add", json={"imdb": "tt9999999"}).status_code == 404


def test_movie_data_is_fetched_once_and_shared(
    alice: TestClient, bob: TestClient, upstream: FakeUpstream, db: Session
) -> None:
    alice.post("/api/movielist/add", json={"imdb": "tt0133093"})
    bob.post("/api/movielist/add", json={"imdb": "tt0133093"})

    assert upstream.count("www.omdbapi.com") == 1
    assert db.scalar(select(func.count()).select_from(Movie)) == 1
