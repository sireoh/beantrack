from database import db

users_collection = db["users"]


def add_user(username: str, password: str):
    print(f"[added user] username: {username}, password: {password}")


def delete_user(username: str):
    print(f"[deleted user] username: {username} ")


def change_password(username: str, new_password: str):
    print(f"[changed password] username: {username}, new_password: {new_password}")
