import django
django.setup()
import os
from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_site.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
})








# import threading
# import django

# # Global lock for thread-safe singleton pattern
# setup_lock = threading.Lock()
# setup_done = False

# def setup_django():
#     global setup_done
#     with setup_lock:
#         if not setup_done:
#             os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_site.settings')
#             django.setup()
#             setup_done = True

# # Ensure Django is set up only once
# setup_django()