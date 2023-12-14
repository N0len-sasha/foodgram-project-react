from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


from .models import (Tag, Ingredient, Recipe, CheckList, Favorites, Follow)
from users.models import CustomUser
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          CheckListSerializer,
                          FavoritesReturnSerializer,
                          FollowSerializer,
                          CustomUserSerializer,
                          CreateRecipeSerializer,)
from .mixims import GetObjectMixim, StandartObjectMixim
from .permissions import IsAuthor
from .filters import CustomSearchFilter, RecipeFilter


class TagViewSet(GetObjectMixim):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(GetObjectMixim):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [CustomSearchFilter,]
    search_fields = ['^name']


class RecipeViewSet(StandartObjectMixim):
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return CreateRecipeSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = [IsAuthenticated]
        elif self.request.method in ['PATCH', 'DELETE']:
            permission_classes = [IsAuthor]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class CheckListViewSet(ModelViewSet):
    queryset = CheckList.objects.all()
    serializer_class = CheckListSerializer
    permission_classes = [IsAuthenticated]


class FavoritesViewSet(ViewSet):
    def create(self, request, **kwargs):
        recipe_id = kwargs.get('recipe_id')
        if not request.user.is_authenticated:
            return Response({'detail': 'Требуется авторизация'},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            return Response({'detail': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)

        favorites, created = Favorites.objects.get_or_create(
            author=request.user)
        if recipe not in favorites.recipe.all():
            favorites.recipe.add(recipe)
            recipe_serializer = FavoritesReturnSerializer(recipe)
            return Response(recipe_serializer.data,
                            status=status.HTTP_201_CREATED)

        return Response({'detail': 'Рецепт уже в избранном'},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        if not request.user.is_authenticated:
            return Response({'detail': 'Требуется авторизация'},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            return Response({'detail': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)

        favorites = Favorites.objects.get(author=self.request.user)
        if recipe in favorites.recipe.all():
            favorites.recipe.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'detail': 'Рецепта нет в избранном'},
                        status=status.HTTP_400_BAD_REQUEST)


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

    def get_permissions(self):
        if self.action == 'me':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
