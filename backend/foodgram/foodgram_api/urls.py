from django.urls import path, include
from rest_framework.routers import SimpleRouter
from djoser.views import TokenCreateView, TokenDestroyView

from .views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    CustomUserViewSet,
)

s_router_v1 = SimpleRouter()
s_router_v1.register(r'tags', TagViewSet, basename='tags')
s_router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
s_router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
s_router_v1.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(s_router_v1.urls)),
    path('auth/token/login/',
         TokenCreateView.as_view(),
         name='token_create'),
    path('auth/token/logout/',
         TokenDestroyView.as_view(),
         name='token_delete'),
    path('', include('djoser.urls')),
]
