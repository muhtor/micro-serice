from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from apps.accounts.models import TBUserToken


@database_sync_to_async
def get_user_token(token):
    try:
        token_user = TBUserToken.objects.get(key=token)
        return token_user.user
    except TBUserToken.DoesNotExist:
        return AnonymousUser()


class QueryAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        scope['user'] = AnonymousUser()
        query_string = scope["query_string"].decode("utf-8")
        if "query=" in query_string:
            user_token = query_string.split("query=")[1]
            scope['user'] = await get_user_token(user_token)
        return await self.app(scope, receive, send)
