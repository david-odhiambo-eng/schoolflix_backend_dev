from .users import router as users_router
from .campus import router as campus_router

__all__ = [
    "users_router",
    "campus_router",
]