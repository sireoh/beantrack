from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.security import Security
from app.db.models import User
from app.core.config import settings
from app.services.auth_service import auth
from app.utils.helpers import Helpers
from app.services.sessions_service import authenticate_user

auth_router = APIRouter()


@auth_router.post("/login")
async def login_route(data: User, response: Response):
    """
    Log in a user and set JWT cookie.

    :param data: The user login data.
    :param response: The response object to set cookie.
    :return: A JSON response with login message.
    """
    try:
        user_id = authenticate_user(data)
        jwt_token = Security.create_jwt_token(user_id)
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            httponly=True,
            secure=not settings.dev_mode,
            samesite="lax",
            max_age=60 * 60 * 24,
        )
        return {"message": "User logged in successfully", "data": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@auth_router.get("/auth")
def auth_route(user_id: str = Depends(Helpers.get_current_user)):
    """
    Get authentication status for the current user.

    :param user_id: The authenticated user ID (injected automatically).
    :return: Authentication data.
    """
    try:
        return auth(user_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@auth_router.post("/logout")
async def logout_route(response: Response):
    """
    Log out the current user by clearing the JWT cookie.

    :param response: The response object to clear cookie.
    :return: Logout message.
    """
    try:
        response.delete_cookie("access_token")
        return {"message": "User logged out"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
