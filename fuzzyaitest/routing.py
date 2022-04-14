from django.urls import path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from game.consumers import GameConsumer

application = ProtocolTypeRouter({
    # WebSocket game handler
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path('game/<int:game_id>', GameConsumer.as_asgi()),
            ])
        )
    ),
})