from datetime import datetime

from pydantic import computed_field

from app.models.enums import Theme, UserRole
from app.schemas.common import ORMModel, RequestModel


class UserOut(ORMModel):
    discord_id: str
    username: str
    avatar: str | None
    created_at: datetime
    last_login: datetime
    role: UserRole
    theme: Theme | None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def avatar_url(self) -> str | None:
        if self.avatar is None:
            return None
        return f"https://cdn.discordapp.com/avatars/{self.discord_id}/{self.avatar}.png"


class ThemeUpdateRequest(RequestModel):
    theme: Theme
