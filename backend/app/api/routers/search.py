from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, Omdb, TvMaze
from app.schemas.search import MediaType, SearchResponse

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
def search(
    media_type: Annotated[MediaType, Query(alias="type")],
    q: Annotated[str, Query(min_length=1, max_length=200)],
    _user: CurrentUser,  # login required: protects the OMDb key's quota
    tvmaze: TvMaze,
    omdb: Omdb,
) -> SearchResponse:
    """Search TVmaze (`type=tv`) or OMDb (`type=movie`)."""
    query = q.strip()
    results = tvmaze.search(query) if media_type is MediaType.TV else omdb.search(query)
    return SearchResponse(type=media_type, query=query, results=results)
