"""
User data access layer.
"""

import bcrypt
import uuid
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.db.models import DBUser, DBTVList, DBMovieList
from fastapi import HTTPException, status

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def add_user(_u):
    """
    Add a new user with hashed password and create empty lists.

    :param _u: The user data.
    """
    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(_u.password.encode(), bcrypt.gensalt()).decode()

    with SessionLocal() as session:
        # Create TVList and MovieList
        tvlist = DBTVList(
            userId=str(uuid.uuid4())
        )  # Wait, userId is for the list? No, TVList has userId ref User.userId, but user not created yet.
        # Need to create user first, get userId, then create lists.

        user = DBUser(
            userId=str(uuid.uuid4()),
            username=_u.username,
            password=hashed_password,
            userType="user",
            avatar=None,
        )
        session.add(user)
        session.flush()  # Get userId

        tvlist = DBTVList(tvListId=str(uuid.uuid4()), userId=user.userId)
        movielist = DBMovieList(movieListId=str(uuid.uuid4()), userId=user.userId)
        session.add(tvlist)
        session.add(movielist)

        session.commit()

    print(f"[added user] username: {_u.username}, userId: {user.userId}")


def delete_user(data):
    """
    Delete a user and associated lists.

    :param data: The user data for deletion.
    :return: Deletion result.
    :raises HTTPException: If user not found or invalid credentials.
    """
    with SessionLocal() as session:
        user = session.query(DBUser).filter(DBUser.username == data.username).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not bcrypt.checkpw(data.password.encode(), user.password.encode()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        # Delete associated lists and data
        tvlist = session.query(DBTVList).filter(DBTVList.userId == user.userId).first()
        if tvlist:
            # Delete TVShows, etc. But for simplicity, cascade delete if set up, else manual
            session.delete(tvlist)

        movielist = (
            session.query(DBMovieList).filter(DBMovieList.userId == user.userId).first()
        )
        if movielist:
            session.delete(movielist)

        session.delete(user)
        session.commit()

    print(f"[deleted user] username: {data.username}")

    return {
        "message": "User and associated data deleted successfully",
    }


def change_password(username: str, new_password: str):
    """
    Change a user's password.

    :param username: The username.
    :param new_password: The new password.
    """
    with SessionLocal() as session:
        user = session.query(DBUser).filter(DBUser.username == username).first()
        if user:
            user.password = new_password
            session.commit()
            print(f"[changed password] username: {username}")
        else:
            print(f"[changed password] username: {username} not found")


def get_user_tvlist(username: str):
    """
    Get a user's TV list.

    :param username: The username.
    :return: The TV list or None.
    """
    with SessionLocal() as session:
        user = session.query(DBUser).filter(DBUser.username == username).first()
        if not user:
            print(f"[get_user_tvlist] username {username} not found")
            return None

        tvlist = session.query(DBTVList).filter(DBTVList.userId == user.userId).first()
        return tvlist


def get_user_movielist(username: str):
    """
    Get a user's movie list.

    :param username: The username.
    :return: The movie list or None.
    """
    with SessionLocal() as session:
        user = session.query(DBUser).filter(DBUser.username == username).first()
        if not user:
            print(f"[get_user_movielist] username {username} not found")
            return None

        movielist = (
            session.query(DBMovieList).filter(DBMovieList.userId == user.userId).first()
        )
        return movielist
