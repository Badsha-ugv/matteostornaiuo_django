# notifications/middleware.py
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.db import close_old_connections
from channels.auth import AuthMiddlewareStack
from channels.middleware import BaseMiddleware

User = get_user_model()

@database_sync_to_async
def get_user(validated_token):
    try:
        user_id = validated_token.get("user_id")
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        close_old_connections()
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]

        if token is None:
            scope["user"] = None
            return await super().__call__(scope, receive, send)

        try:
            validated_token = UntypedToken(token)
            scope["user"] = await get_user(validated_token)
        except (InvalidToken, TokenError):
            scope["user"] = None

        return await super().__call__(scope, receive, send)

def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))