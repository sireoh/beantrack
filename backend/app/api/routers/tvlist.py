from fastapi import APIRouter, Response, status

from app.api.deps import CurrentUser, DbSession, TvMaze
from app.schemas.common import ImdbId
from app.schemas.tvlist import (
    TvListAddRequest,
    TvListEntryOut,
    TvListOut,
)
from app.services import lists as list_service

router = APIRouter(prefix="/tvlist", tags=["tvlist"])


@router.get("", response_model=TvListOut)
def get_tvlist(user: CurrentUser, db: DbSession) -> TvListOut:
    """The logged-in user's full TV list."""
    return TvListOut.model_validate(list_service.get_tvlist(db, user))


@router.post("/add", response_model=TvListEntryOut, status_code=status.HTTP_201_CREATED)
def add_to_tvlist(
    body: TvListAddRequest, user: CurrentUser, db: DbSession, tvmaze: TvMaze
) -> TvListEntryOut:
    """Add a show from the supplied catalog data to the logged-in user's TV list."""
    entry = list_service.add_tvshow(db, tvmaze=tvmaze, user=user, request=body)
    return TvListEntryOut.model_validate(entry)


@router.delete("/{imdb}", status_code=status.HTTP_204_NO_CONTENT)
def delete_from_tvlist(imdb: ImdbId, user: CurrentUser, db: DbSession) -> Response:
    """Remove a show from the logged-in user's TV list."""
    list_service.delete_tvshow(db, user=user, imdb=imdb)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
