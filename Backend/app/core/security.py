from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings


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
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
        if settings.dev_mode == "true":
            print(f"jwt_token: {encoded_jwt}")
        return encoded_jwt
