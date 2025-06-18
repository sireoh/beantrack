from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status, Response, Cookie
from database import db  # assuming you're importing db from your database setup
from helpers import Helpers
from models import User
import bcrypt

sessions_collection = db["sessions"]
users_collection = db["users"]


def add_session(data: User):
    found_user = users_collection.find_one({"username": data.username})

    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not bcrypt.checkpw(data.password.encode(), found_user["password"].encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Check if a session already exists for this user
    existing_session = sessions_collection.find_one({"user": found_user["_id"]})
    if existing_session:
        return {"is_logged_in": True, "message": "User is already logged in"}

    # Create a new session
    session_doc = {
        "user": found_user["_id"],
        "date": datetime.now(),
    }

    result = sessions_collection.insert_one(session_doc)
    print(f"[added session] user: {data.username}, session_id: {result.inserted_id}")
    return {
        "is_logged_in": False,
        "message": "Session created",
        "session_id": str(result.inserted_id),
    }


def delete_session(response: Response, session_token: str = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=400, detail="No session token provided")

    try:
        session_id = Helpers.verify_signed_token(session_token)
    except HTTPException:
        # Optional: still clear cookie if invalid
        response.delete_cookie("session_token")
        raise

    # Delete session from DB
    result = sessions_collection.delete_one({"_id": ObjectId(session_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")

    # Clear cookie
    response.delete_cookie("session_token")

    print(f"[logout] session {session_id} deleted")
    return {"message": "User logged out"}
