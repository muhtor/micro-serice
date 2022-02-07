import os
from django.urls import re_path

from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tbserver.settings')
django_asgi_app = get_asgi_application()


from channels.routing import ProtocolTypeRouter, URLRouter

from apps.orders.consumers import OrderControlConsumer
from apps.addresses.consumers import RetrieveUserLocationConsumer
from apps.core.middleware import QueryAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": QueryAuthMiddleware(
        URLRouter(
                [
                    re_path(r'^dashboard/user-location-list/$', RetrieveUserLocationConsumer.as_asgi()),
                    re_path(r'^order/offer-list/$', OrderControlConsumer.as_asgi()),
                ]
            ))
})
