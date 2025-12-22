from fastapi import Request
from ..core.database import engine
from jose import JWTError, jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import sessionmaker
from ..db.models import TVList, MovieList
from ..core.config import settings

SECRET_KEY = settings.secret_key
DEV_MODE = settings.dev_mode

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Helpers:
    """
    Utility class for helper functions.
    """

    @staticmethod
    def get_current_tvlist_id(user_id: str) -> str:
        """
        Get the TV list ID for the user.

        :param user_id: The user ID.
        :return: The TV list ID.
        :raises HTTPException: If not found.
        """
        with SessionLocal() as session:
            tvlist = session.query(TVList).filter(TVList.userId == user_id).first()
            if not tvlist:
                raise HTTPException(status_code=404, detail="TV list not found")
            return str(tvlist.tvListId)

    @staticmethod
    def get_current_movielist_id(user_id: str) -> str:
        """
        Get the movie list ID for the user.

        :param user_id: The user ID.
        :return: The movie list ID.
        :raises HTTPException: If not found.
        """
        with SessionLocal() as session:
            movielist = (
                session.query(MovieList).filter(MovieList.userId == user_id).first()
            )
            if not movielist:
                raise HTTPException(status_code=404, detail="Movie list not found")
            return str(movielist.movieListId)

    @staticmethod
    def get_current_user(request: Request) -> str:
        """
        Dependency function to get the current authenticated user ID from JWT.

        :param request: The request object.
        :return: The user ID.
        :raises HTTPException: If not authenticated or invalid token.
        """
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id: str = payload.get("sub")  # type: ignore
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                )
            return user_id
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
