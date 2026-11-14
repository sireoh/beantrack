from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession, Omdb
from app.schemas.movielist import MovieListAddRequest, MovieListEntryOut, MovieListOut
from app.services import lists as list_service

router = APIRouter(prefix="/movielist", tags=["movielist"])


@router.get("", response_model=MovieListOut)
def get_movielist(user: CurrentUser, db: DbSession) -> MovieListOut:
    """The logged-in user's full movie list."""
    return MovieListOut.model_validate(list_service.get_movielist(db, user))


@router.post("/add", response_model=MovieListEntryOut, status_code=status.HTTP_201_CREATED)
def add_to_movielist(
    body: MovieListAddRequest, user: CurrentUser, db: DbSession, omdb: Omdb
) -> MovieListEntryOut:
    """Add a movie (by IMDb id) to the logged-in user's movie list."""
    entry = list_service.add_movie(db, omdb=omdb, user=user, request=body)
    return MovieListEntryOut.model_validate(entry)
