from fastapi import Depends, FastAPI

from app.core.dependencies.auth import require_roles
from app.middleware.auth import AuthMiddleware
from .config.settings import TORTOISE_ORM, settings
from tortoise.contrib.fastapi import register_tortoise
from app.routes.v1 import users_router, campus_router

app = FastAPI(
    docs_url="/",
    title="SchoolFlix",
    version=settings.VERSION
)
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,
    add_exception_handlers=True,
)
app.add_middleware(AuthMiddleware)
app.include_router(users_router, prefix=f"/{settings.VERSION}/users", tags=["Accounts"])
app.include_router(campus_router, prefix=f"/{settings.VERSION}/campuses", tags=["Campus"])


@app.get("/admin-only")
async def admin_route(current_user = Depends(require_roles("admin"))):
    return {"message": "welcome admin", "user": current_user.email}