from django.shortcuts import render, get_object_or_404
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter


from .models import (Tag, Ingredient, Recipe, CheckList, Favorites, Follow)
from users.models import CustomUser
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          CheckListSerializer,
                          FavoritesSerializer,
                          FollowSerializer,
                          CustomUserSerializer,
                          CreateRecipeSerializer)
from .mixims import GetObjectMixim, StandartObjectMixim, DeleteAndPostMixim


class TagViewSet(GetObjectMixim):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class CustomSearchFilter(SearchFilter):
    def get_search_terms(self, request):
        return request.query_params.get('name', '')


class IngredientViewSet(GetObjectMixim):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [CustomSearchFilter,]
    search_fields = ['^name']


class RecipeViewSet(StandartObjectMixim):
    queryset = Recipe.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ('get', 'post', 'patch', 'delete')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateRecipeSerializer
        return RecipeSerializer


class CheckListViewSet(ModelViewSet):
    queryset = CheckList.objects.all()
    serializer_class = CheckListSerializer
    permission_classes = [IsAuthenticated]


class FavoritesViewSet(DeleteAndPostMixim):
    queryset = Favorites.objects.all()
    serializer_class = FavoritesSerializer
    permission_classes = [IsAuthenticated]

    # def perform_create(self, serializer):
    #     recipe_id = self.kwargs.get(self.pk_url_kwargs)
    #     serializer.save(recipe=Recipe.objects.get(id=recipe_id))


class FollowViewSet(ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


'''Пользователи'''


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [AllowAny]

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
