from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError

from app.models.index import User
from app.security.authentication import decode_token
from app.services.users import is_token_blacklisted


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Tries to attach `request.state.user` if a valid Bearer token exists.
    It does NOT reject the request if token is invalid — route dependencies handle enforcement.
    """
    async def dispatch(self, request, call_next):
        request.state.user = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()
            try:
                payload = decode_token(token)
                jti = payload.get("jti")
                if not await is_token_blacklisted(jti):
                    sub = payload.get("sub")
                    if sub:
                        user = await User.get_or_none(email=sub)
                        if user:
                            request.state.user = user
            except JWTError:
                request.state.user = None
        return await call_next(request)
