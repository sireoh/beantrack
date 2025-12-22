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


def signup(_u):
    """
    Add a new user with hashed password and create empty lists.

    :param _u: The user data.
    """
    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(_u.password.encode(), bcrypt.gensalt()).decode()

    with SessionLocal() as session:
        user = DBUser(
            user_id=str(uuid.uuid4()),
            username=_u.username,
            password=hashed_password,
            user_type="user",
            avatar=None,
        )
        session.add(user)
        session.flush()  # Get user_id

        tvlist = DBTVList(tv_list_id=str(uuid.uuid4()), user_id=user.user_id)
        movielist = DBMovieList(movie_list_id=str(uuid.uuid4()), user_id=user.user_id)
        session.add(tvlist)
        session.add(movielist)

        session.commit()

        # Store user_id before session closes
        user_id = user.user_id

    print(f"[added user] username: {_u.username}, userId: {user_id}")


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

        tvlist = session.query(DBTVList).filter(DBTVList.userid == user.userid).first()
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
            session.query(DBMovieList).filter(DBMovieList.userid == user.userid).first()
        )
        return movielist
