import csv
from collections import defaultdict

from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, mixins, viewsets, views


from .models import (Tag, Ingredient, Recipe, CheckList, Favorites)
from users.models import FoodgramUser, Follow
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          RecipeReturnSerializer,
                          ReturnSerializer,
                          UserSerializer,
                          CreateRecipeSerializer,)
from .pagination import CustomPageNumberPagination
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
    filter_backends = [CustomSearchFilter, ]
    search_fields = ['^name', ]


class RecipeViewSet(StandartObjectMixim):
    queryset = Recipe.objects.all()
    pagination_class = CustomPageNumberPagination
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
            if is_in_shopping_cart is not None and int(
               is_in_shopping_cart) == 1:
                try:
                    checklists = self.request.user.checklist
                    recipe_ids_in_checklists = checklists.values_list(
                        'recipe__id', flat=True
                    )
                    return Recipe.objects.filter(
                        id__in=recipe_ids_in_checklists
                    )
                except CheckList.DoesNotExist:
                    return Recipe.objects.none()

            if is_favorited is not None and int(is_favorited) == 1:
                try:
                    favorites = Favorites.objects.get(user=self.request.user)
                    return favorites.recipe
                except Favorites.DoesNotExist:
                    return Recipe.objects.none()

        return queryset

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

        checklists = self.request.user.checklist
        recipe_ids_in_checklists = checklists.values_list(
            'recipe__id', flat=True
        )

        if recipe not in recipe_ids_in_checklists:
            CheckList.objects.get_or_create(user=self.request.user,
                                            recipe=recipe)
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
            checklist = CheckList.objects.get(user=self.request.user,
                                              recipe=recipe)
        except CheckList.DoesNotExist:
            return Response({'detail':
                             'Такого рецепта не было добавлено в чек лист'},
                            status=status.HTTP_400_BAD_REQUEST)

        checklist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

        favorites = self.request.user.favorites
        recipe_ids_in_favorites = favorites.values_list(
            'recipe__id', flat=True
        )

        if recipe not in recipe_ids_in_favorites:
            favorites, created = Favorites.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
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
            favorites = Favorites.objects.get(user=self.request.user,
                                              recipe=recipe)
        except Favorites.DoesNotExist:
            return Response({'detail': 'Данного рецепта нет в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)

        favorites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(ViewSet):

    def create(self, request, **kwargs):
        user_id = kwargs.get('user_id')

        try:
            follow_user = FoodgramUser.objects.get(id=user_id)
        except FoodgramUser.DoesNotExist:
            return Response({'detail': 'Пользователь не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        if follow_user == self.request.user:
            return Response({'detail': 'Нельзя подписаться на самого себя'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated:
            return Response({'detail': 'Требуется авторизация'},
                            status=status.HTTP_401_UNAUTHORIZED)

        followings = self.request.user.following
        recipe_ids_in_foolowing = followings.values_list(
            'user_follow__id', flat=True
        )

        if follow_user not in recipe_ids_in_foolowing:
            Follow.objects.get_or_create(
                user=request.user,
                user_follow=follow_user
            )
            recipe_serializer = ReturnSerializer(follow_user,
                                                 context={'request': self.request})
            return Response(recipe_serializer.data,
                            status=status.HTTP_201_CREATED)

        return Response({'detail': 'Вы уже подписаны на этого пользователя'},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        if not request.user.is_authenticated:
            return Response({'detail': 'Требуется авторизация'},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            follow_user = FoodgramUser.objects.get(id=user_id)
        except FoodgramUser.DoesNotExist:
            return Response({'detail': 'Пользователь не существует'},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            follows = Follow.objects.get(user=self.request.user,
                                         user_follow=follow_user)
        except Follow.DoesNotExist:
            return Response({'detail': 'Такого пользователя нет в подписках'},
                            status=status.HTTP_400_BAD_REQUEST)

        follows.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = FoodgramUser.objects.all()
    serializer_class = ReturnSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        followers_ids = self.request.user.following.values_list('user_follow',
                                                                flat=True)
        return FoodgramUser.objects.filter(id__in=followers_ids)


class DownloadShoppingCartView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = self.request.user
        checklist = CheckList.objects.get(user=user)
        recipes = checklist.recipe.all()

        ingredient_totals = defaultdict(int)

        for recipe in recipes:
            for recipe_ingredient in recipe.recipeingredient.all():
                ingredient = recipe_ingredient.ingredient
                amount = recipe_ingredient.amount

                ingredient_totals[ingredient] += amount

        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = ('attachment;'
                                           'filename="Ingredients.csv"')
        writer = csv.DictWriter(response, fieldnames=['Ингредиент',
                                                      'Количество',
                                                      'Мера'])
        writer.writeheader()

        for ingredient, total_amount in ingredient_totals.items():
            writer.writerow({
                'Ингредиент': ingredient.name,
                'Количество': total_amount,
                'Мера': ingredient.measurement_unit
            })

        return response


'''Пользователи'''


class CustomUserViewSet(UserViewSet):
    queryset = FoodgramUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        return FoodgramUser.objects.all()

    # def get_object(self):
    #     queryset = self.get_queryset()
    #     user = get_object_or_404(queryset, id=self.kwargs['id'])
    #     return user

    # def get_serializer_class(self):
    #     if self.action == 'me':
    #         return UserSerializer
    #     return super().get_serializer_class()
