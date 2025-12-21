import os
from datetime import datetime, timedelta
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import Request
from .database import db
from jose import JWTError, jwt
from fastapi import HTTPException, status


load_dotenv()
MONGODB_URI = os.environ["MONGODB_URI"]
SECRET_KEY = os.environ["SECRET_KEY"]
DEV_MODE = os.environ["DEV_MODE"]

users_collection = db["users"]


class Helpers:
    """
    Utility class for helper functions.
    """

    @staticmethod
    def get_current_user(request: Request) -> str:
        """
        Dependency function to get the current authenticated user ID from JWT.

        :param request: The request object.
        :return: The user ID.
        :raises HTTPException: If not authenticated or invalid token.
        """
        return Helpers.get_current_user_id_from_jwt(request)

    @staticmethod
    def create_jwt_token(user_id: str) -> str:
        """
        Create a JWT token for the user.

        :param user_id: The user ID to encode in the token.
        :return: The JWT token.
        """
        expire = datetime.utcnow() + timedelta(days=1)  # 24 hours
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
        if DEV_MODE == "true":
            print(f"jwt_token: {encoded_jwt}")
        return encoded_jwt

    @staticmethod
    def verify_jwt_token(token: str) -> str:
        """
        Verify a JWT token and return the user ID.

        :param token: The JWT token to verify.
        :return: The user ID if valid.
        :raises HTTPException: If invalid.
        """
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

    @staticmethod
    def get_current_user_id_from_jwt(request: Request) -> str:
        """
        Get the current user ID from the JWT token in the request.

        :param request: The request object.
        :return: The user ID.
        :raises HTTPException: If not authenticated or invalid token.
        """
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        return Helpers.verify_jwt_token(token)

    @staticmethod
    def get_current_tvlist_id(user_id: str) -> ObjectId:
        """
        Get the TV list ID for the user.

        :param user_id: The user ID.
        :return: The TV list ObjectId.
        :raises HTTPException: If not found.
        """
        user_doc = users_collection.find_one({"_id": ObjectId(user_id)})

        if not user_doc or "tvlist" not in user_doc:
            raise HTTPException(status_code=404, detail="TV list not found")

        return user_doc["tvlist"]

    @staticmethod
    def get_current_movielist_id(user_id: str) -> ObjectId:
        """
        Get the movie list ID for the user.

        :param user_id: The user ID.
        :return: The movie list ObjectId.
        :raises HTTPException: If not found.
        """
        user_doc = users_collection.find_one({"_id": ObjectId(user_id)})

        if not user_doc or "movielist" not in user_doc:
            raise HTTPException(status_code=404, detail="Movie list not found")

        return user_doc["movielist"]
