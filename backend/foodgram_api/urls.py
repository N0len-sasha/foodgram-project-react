from django.urls import path, include
from rest_framework.routers import SimpleRouter
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    CustomUserViewSet,
    FavoritesViewSet,
    FollowViewSet,
    SubscriptionsViewSet,
    CheckListViewSet,
    DownloadShoppingCartView
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
s_router_v1.register(r'recipes/(?P<recipe_id>\d+)/favorite',
                     FavoritesViewSet,
                     basename='favorites'),
s_router_v1.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                     CheckListViewSet,
                     basename='shopping_cart')
s_router_v1.register(r'users/subscriptions',
                     SubscriptionsViewSet,
                     basename='subscriptions')
s_router_v1.register(r'users',
                     CustomUserViewSet,
                     basename='users')
s_router_v1.register(r'users/(?P<user_id>\d+)/subscribe',
                     FollowViewSet,
                     basename='subscribe'),

urlpatterns = [
    path('recipes/download_shopping_cart/',
         DownloadShoppingCartView.as_view(),
         name='download'),
    path('', include(s_router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
