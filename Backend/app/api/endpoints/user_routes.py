from fastapi import APIRouter, HTTPException, status

from app.db.models import User, SignupRequest
from app.services.user_service import add_user
from app.utils.helpers import Helpers

user_router = APIRouter()


@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def add_user_route(signup_data: SignupRequest):
    """
    Add a new user to the system.

    :param signup_data: The signup data containing username and password.
    :return: A JSON response with the added user data.
    """
    try:
        user_data = User(
            userId=Helpers.generate_uuid(),
            username=signup_data.username,
            password=signup_data.password,
            userType="user",
            avatar="",
        )
        add_user(user_data)
        return {"message": "User added successfully", "user_data": user_data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
