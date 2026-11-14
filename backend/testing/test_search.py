from fastapi.testclient import TestClient

from testing.fakes import OMDB_TEST_KEY, FakeUpstream


def test_search_tv_uses_tvmaze(alice: TestClient, upstream: FakeUpstream) -> None:
    response = alice.get("/api/search", params={"type": "tv", "q": "breaking"})

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["type"] == "tv" and body["query"] == "breaking"
    assert body["results"] == [
        {
            "imdb": "tt0903747",
            "title": "Breaking Bad",
            "year": "2008",
            "image": "https://static.tvmaze.com/bb-original.jpg",
            "score": 9.2,
        },
        {
            "imdb": None,  # TVmaze knows no IMDb id for this one
            "title": "Breaking Bad: Obscure Web Series",
            "year": None,
            "image": None,
            "score": None,
        },
    ]
    request = upstream.requests[-1]
    assert request.url.host == "api.tvmaze.com"
    assert request.url.params["q"] == "breaking"


def test_search_movie_uses_omdb_with_api_key(alice: TestClient, upstream: FakeUpstream) -> None:
    response = alice.get("/api/search", params={"type": "movie", "q": "matrix"})

    assert response.status_code == 200, response.text
    assert response.json()["results"] == [
        {
            "imdb": "tt0133093",
            "title": "The Matrix",
            "year": "1999",
            "image": "https://m.media-amazon.com/matrix.jpg",
            "score": None,
        }
    ]
    request = upstream.requests[-1]
    assert request.url.host == "www.omdbapi.com"
    assert request.url.params["s"] == "matrix"
    assert request.url.params["apikey"] == OMDB_TEST_KEY


def test_search_movie_with_no_results(alice: TestClient) -> None:
    response = alice.get("/api/search", params={"type": "movie", "q": "zzzz"})

    assert response.status_code == 200
    assert response.json()["results"] == []


def test_search_validates_params(alice: TestClient) -> None:
    assert alice.get("/api/search", params={"type": "book", "q": "x"}).status_code == 422
    assert alice.get("/api/search", params={"type": "tv"}).status_code == 422
    assert alice.get("/api/search", params={"type": "tv", "q": ""}).status_code == 422


def test_search_upstream_failure_is_502(alice: TestClient, upstream: FakeUpstream) -> None:
    upstream.fail_hosts.add("www.omdbapi.com")

    assert alice.get("/api/search", params={"type": "movie", "q": "matrix"}).status_code == 502
