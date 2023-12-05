from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from .models import (Tag, Ingredient, Recipe, CheckList, Favorites, Follow)
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          CheckListSerializer,
                          FavoritesSerializer,
                          FollowSerializer)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class CheckListViewSet(ModelViewSet):
    queryset = CheckList.objects.all()
    serializer_class = CheckListSerializer


class FavoritesViewSet(ModelViewSet):
    queryset = Favorites.objects.all()
    serializer_class = FavoritesSerializer


class FollowViewSet(ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
