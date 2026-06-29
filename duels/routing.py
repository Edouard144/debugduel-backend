from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/duels/(?P<room_code>\w+)/$', consumers.DuelConsumer.as_asgi()),
]
