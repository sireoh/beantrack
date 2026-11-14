"""Domain errors raised by services and clients, mapped to HTTP responses in `app.main`.

Services never import FastAPI; they raise these and the API layer translates them.
"""


class AppError(Exception):
    status_code: int = 400

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class InvalidRequestError(AppError):
    status_code = 422


class AuthenticationError(AppError):
    status_code = 401


class UpstreamError(AppError):
    """An external API (TVmaze, OMDb, Discord) failed or returned something unusable."""

    status_code = 502
