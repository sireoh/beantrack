import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import jwt

load_dotenv()
SECRET_KEY = os.environ["SECRET_KEY"]
DEV_MODE = os.environ["DEV_MODE"]


class Security:
    """
    Utility class for helper functions.
    """

    @staticmethod
    def create_jwt_token(user_id: str) -> str:
        """
        Create a JWT token for the user.

        :param user_id: The user ID to encode in the token.
        :return: The JWT token.
        """
        expire = datetime.now() + timedelta(days=1)  # 24 hours
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.now(),
        }
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
        if DEV_MODE == "true":
            print(f"jwt_token: {encoded_jwt}")
        return encoded_jwt
