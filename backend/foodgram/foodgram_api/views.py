from django.shortcuts import render, get_object_or_404
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet

from .models import (Tag, Ingredient, Recipe, CheckList, Favorites, Follow)
from users.models import CustomUser
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          CheckListSerializer,
                          FavoritesSerializer,
                          FollowSerializer,
                          CustomUserSerializer,
                          CustomUserCreateSerializer)
from .mixims import GetObjectMixim


class TagViewSet(GetObjectMixim):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(GetObjectMixim):
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


'''Пользователи'''


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, id=self.kwargs['id'])
        return user

    def get_serializer_class(self):
        if self.action == 'me':
            return CustomUserSerializer
        return super().get_serializer_class()
