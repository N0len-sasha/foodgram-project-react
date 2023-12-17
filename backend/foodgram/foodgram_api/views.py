from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, mixins, viewsets, views


from .models import (Tag, Ingredient, Recipe, CheckList, Favorites, Follow)
from users.models import CustomUser
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          RecipeReturnSerializer,
                          FollowReturnSerializer,
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

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        is_favorited = self.request.query_params.get('is_favorited')
        if self.request.user.is_authenticated:
            if is_in_shopping_cart is not None and int(is_in_shopping_cart) == 1:
                try:
                    checklist = CheckList.objects.get(author=self.request.user)
                    return checklist.recipe
                except CheckList.DoesNotExist:
                    return Recipe.objects.none()

            if is_favorited is not None and int(is_favorited) == 1:
                try:
                    favorites = Favorites.objects.get(author=self.request.user)
                    return favorites.recipe
                except Favorites.DoesNotExist:
                    return Recipe.objects.none()

        return queryset

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


class CheckListViewSet(ViewSet):
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

        checklist, created = CheckList.objects.get_or_create(
            author=request.user)
        if recipe not in checklist.recipe.all():
            checklist.recipe.add(recipe)
            recipe_serializer = RecipeReturnSerializer(recipe)
            return Response(recipe_serializer.data,
                            status=status.HTTP_201_CREATED)

        return Response({'detail': 'Рецепт уже в чеклисте'},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        if not request.user.is_authenticated:
            return Response({'detail': 'Требуется авторизация'},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            return Response({'detail': 'Рецепт не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            checklist = CheckList.objects.get(author=self.request.user)
        except CheckList.DoesNotExist:
            return Response({'detail':
                             'Такого рецепта не было добавлено в чек лист'},
                            status=status.HTTP_400_BAD_REQUEST)

        if recipe in checklist.recipe.all():
            checklist.recipe.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'detail': 'Рецепта нет в чеклисте'},
                        status=status.HTTP_404_NOT_FOUND)


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
            recipe_serializer = RecipeReturnSerializer(recipe)
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
                            status=status.HTTP_404_NOT_FOUND)
        try:
            favorites = Favorites.objects.get(author=self.request.user)
        except Favorites.DoesNotExist:
            return Response({'detail': 'Данного рецепта нет в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)

        if recipe in favorites.recipe.all():
            favorites.recipe.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'detail': 'Рецепта нет в избранном'},
                        status=status.HTTP_404_NOT_FOUND)


class FollowViewSet(ViewSet):

    def create(self, request, **kwargs):
        user_id = kwargs.get('user_id')

        try:
            follow_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'Пользователь не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        if follow_user == self.request.user:
            return Response({'detail': 'Нельзя подписаться на самого себя'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated:
            return Response({'detail': 'Требуется авторизация'},
                            status=status.HTTP_401_UNAUTHORIZED)

        follow, created = Follow.objects.get_or_create(
            author=request.user)
        if follow_user not in follow.user_follow.all():
            follow.user_follow.add(follow_user)
            recipe_serializer = FollowReturnSerializer(
                follow_user,
                context={'request': request}
            )
            return Response(recipe_serializer.data,
                            status=status.HTTP_201_CREATED)

        return Response({'detail': 'Вы уже подписаны на этого пользователя'},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        if not request.user.is_authenticated:
            return Response({'detail': 'Требуется авторизация'},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            follow_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'Пользователь не существует'},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            follows = Follow.objects.get(author=self.request.user)
        except Follow.DoesNotExist:
            return Response({'detail': 'Такого пользователя нет в подписках'},
                            status=status.HTTP_400_BAD_REQUEST)

        if follow_user in follows.user_follow.all():
            follows.user_follow.remove(follow_user)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'detail': 'Пользователя нет в подписках'},
                        status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = FollowReturnSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        follows = Follow.objects.get(author=self.request.user.id)
        user_ids = follows.user_follow.values_list('id', flat=True)
        return CustomUser.objects.filter(id__in=user_ids)


class DownloadShoppingCartView(views.View):
    def get(self, request, *args, **kwargs):
        content = b""
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="Ingredients.txt"')

        return response


'''Пользователи'''


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [AllowAny]

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
