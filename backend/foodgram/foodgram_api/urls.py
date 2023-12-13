from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    CustomUserViewSet,
    FavoritesViewSet
)

s_router_v1 = SimpleRouter()
s_router_v1.register(r'tags',
                     TagViewSet,
                     basename='tags')
s_router_v1.register(r'ingredients',
                     IngredientViewSet,
                     basename='ingredients')
s_router_v1.register(r'recipes',
                     RecipeViewSet,
                     basename='recipes')
s_router_v1.register(r'users',
                     CustomUserViewSet,
                     basename='users')
s_router_v1.register(r'recipes/(?P<recipe_id>\d+)/favorite',
                     FavoritesViewSet,
                     basename='favorites')

urlpatterns = [
    path('', include(s_router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
