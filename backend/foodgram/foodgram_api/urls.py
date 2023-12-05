from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    TagViewSet
)

s_router_v1 = SimpleRouter()
s_router_v1.register(r'tags', TagViewSet, basename='tags')
s_router_v1.register(r'recipes', TagViewSet, basename='recipes')

urlpatterns = [
    path('v1/', include(s_router_v1.urls)),
]
