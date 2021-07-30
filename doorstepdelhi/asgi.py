"""
ASGI config for doorstepdelhi project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, get_default_application
from channels.security.websocket import AllowedHostsOriginValidator

import django
from django.core.asgi import get_asgi_application

import room.routing
import core.routing
import webtraffic.routing
from doorstepdelhi.middleware import TokenAuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "doorstepdelhi.settings")
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter(
                room.routing.websocket_urlpatterns +
                core.routing.websocket_urlpatterns +
                webtraffic.routing.websocket_urlpatterns
            )
        )
    ),
})