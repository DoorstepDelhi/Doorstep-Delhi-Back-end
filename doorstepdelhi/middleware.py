from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token
from urllib import parse

from channels.auth import AuthMiddlewareStack


@database_sync_to_async
def get_user(token_key):
    try:
        token = Token.objects.get(key=token_key)
        print(token.user.username)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            scope['user'] = await get_user(headers)
            try:
                token_name, token_key = headers[b'authorization'].decode().split()
                if token_name == 'Token':
                    scope['user'] = await get_user(token_key)
            except:
                pass
        query_string = scope["query_string"]
        try:
            query_dict = parse.parse_qs(query_string.decode('utf-8'))
            token = query_dict.get('token')
            token = token[0]
            scope['user'] = await get_user(token)
        except:
            pass
        return await self.inner(scope, receive, send)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
