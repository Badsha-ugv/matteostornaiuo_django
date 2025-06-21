"""
ASGI config for project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from dashboard.middleware import JWTAuthMiddlewareStack
from dashboard.routing import websocket_urlpatterns
from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from channels.auth import AuthMiddlewareStack


from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')



# application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddlewareStack(
        # AuthMiddlewareStack(
        # )
            URLRouter([
                *websocket_urlpatterns,
                *chat_websocket_urlpatterns
            ])
    ),
})