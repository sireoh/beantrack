from fastapi import APIRouter

from .endpoints.user_routes import user_router
from .endpoints.auth_routes import auth_router
from .endpoints.search_routes import search_router
from .endpoints.tvshows_routes import tvshows_router
from .endpoints.movies_routes import movies_router

router = APIRouter(prefix="/api/v1")

router.include_router(user_router)
router.include_router(auth_router)
router.include_router(search_router)
router.include_router(tvshows_router)
router.include_router(movies_router)
