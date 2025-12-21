import hmac
import hashlib
import base64
import os
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import HTTPException, Request, status
from database import db

load_dotenv()
MONGODB_URI = os.environ["MONGODB_URI"]
SECRET_KEY = os.environ["SECRET_KEY"]
DEV_MODE = os.environ["DEV_MODE"]

sessions_collection = db["sessions"]
users_collection = db["users"]


class Helpers:
    """
    Utility class for helper functions.
    """

    @staticmethod
    def create_empty_list_doc(collection):
        """
        Create an empty list document with an empty data array and return its ObjectId.

        :param collection: The MongoDB collection.
        :return: The inserted document's ObjectId.
        """
        res = collection.insert_one({"data": []})
        return res.inserted_id

    @staticmethod
    def sign_session_id(session_id: str):
        """
        Sign a session ID with HMAC-SHA256.

        :param session_id: The session ID to sign.
        :return: The signed token.
        """
        key_bytes = SECRET_KEY.encode()  # Convert string to bytes
        signature = hmac.new(key_bytes, session_id.encode(), hashlib.sha256).digest()
        signed_token = f"{session_id}.{base64.urlsafe_b64encode(signature).decode()}"
        if DEV_MODE == "true":
            print(f"signed_token: {signed_token}")
        return signed_token

    @staticmethod
    def verify_signed_token(signed_token: str):
        """
        Verify a signed token.

        :param signed_token: The signed token to verify.
        :return: The session ID if valid.
        :raises HTTPException: If invalid.
        """
        try:
            session_id, signature_b64 = signed_token.split(".")
            expected_signature = hmac.new(
                SECRET_KEY.encode(), session_id.encode(), hashlib.sha256
            ).digest()
            actual_signature = base64.urlsafe_b64decode(signature_b64)

            if not hmac.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid session signature")

            return session_id
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or malformed session token",
            )

    @staticmethod
    def get_current_user_id_from_session(request: Request):
        """
        Get the current user ID from the session token in the request.

        :param request: The request object.
        :return: The user ID.
        :raises HTTPException: If not authenticated or invalid session.
        """
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        try:
            session_id = Helpers.verify_signed_token(session_token)
            session = sessions_collection.find_one({"_id": ObjectId(session_id)})
            if not session:
                raise HTTPException(status_code=401, detail="Invalid session")
            return session["user"]
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid session")

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
