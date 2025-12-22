from fastapi import APIRouter, HTTPException, Response, status

from app.db.models import User
from app.services.user_service import add_user, delete_user

user_router = APIRouter()


@user_router.post("/user/add", status_code=status.HTTP_201_CREATED)
async def add_user_route(user_data: User):
    """
    Add a new user to the system.

    :param user_data: The user data to add.
    :return: A JSON response with the added user data.
    """
    try:
        add_user(user_data)
        return {"message": "User added successfully", "user_data": user_data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@user_router.delete("/user/delete")
async def delete_user_route(data: User):
    """
    Delete a user from the system.

    :param data: The user data to delete.
    :return: No content on success.
    """
    try:
        delete_user(data)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
