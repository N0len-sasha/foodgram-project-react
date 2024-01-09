from djoser.views import UserViewSet
from django.http import FileResponse
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import action

from .models import (Tag, Ingredient, Recipe,
                     CheckList, Favorites, RecipeIngredient)
from users.models import FoodgramUser
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          FollowSerializer,
                          ReturnRecipesCountSerializer,
                          UserSerializer,
                          FavoritesSerializer,
                          CreateRecipeSerializer,
                          CheckListSerializer)
from .pagination import PageNumberPagination
from .permissions import IsAuthorOrReadOnly
from .filters import IngredientSearchFilter, RecipeFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter, )
    search_fields = ('^name', )


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'ingredients').all()
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    @staticmethod
    def create_object(serializer_class, pk, request):
        create_data = {
            'user': request.user.id,
            'recipe': pk
        }
        context = {'request': request}
        serializer = serializer_class(data=create_data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_object(model, pk, request):

        obj = model.objects.filter(recipe_id=pk, user=request.user)
        if not obj.exists():
            return Response({'detail': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def write_txt_data(ingredients):
        data = ''

        for ingredient in ingredients:
            row = (
                f'{ingredient["ingredient__name"]}, '
                f'{ingredient["total_amount"]}, '
                f'{ingredient["ingredient__measurement_unit"]}'
            )
            data += (row + ' || ')

        return data

    @action(detail=True, methods=['post'],
            url_path='favorite', permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        return self.create_object(FavoritesSerializer, pk, request)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_object(Favorites, pk, request)

    @action(detail=True, methods=['post'],
            url_path='shopping_cart', permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        return self.create_object(CheckListSerializer, pk, request)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_object(CheckList, pk, request)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__checklist__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        data = self.write_txt_data(ingredients)

        return FileResponse(data,
                            as_attachment=True,
                            content_type='text/plain',
                            filename='Ingredients.txt')


class FoodgramUserViewSet(UserViewSet):
    queryset = FoodgramUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=['post'],
            url_path='subscribe', permission_classes=(IsAuthenticated,))
    def follow(self, request, id):

        if not FoodgramUser.objects.filter(id=id).exists():
            return Response({'detail': 'Пользователя не существует'},
                            status=status.HTTP_404_NOT_FOUND)

        create_data = {
            'subscriber': request.user.id,
            'recipe_owner': id
        }
        context = {'request': request}
        serializer = FollowSerializer(data=create_data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'],
            url_path='subscriptions', permission_classes=(IsAuthenticated,))
    def subscribtions(self, request):
        queryset = FoodgramUser.objects.filter(
            recipeauthor__subscriber=self.request.user
        )
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ReturnRecipesCountSerializer(result_page,
                                                  many=True,
                                                  context={'request': request})

        return paginator.get_paginated_response(serializer.data)

    @follow.mapping.delete
    def delete_subscribtions(self, request, id):

        follow = request.user.subscriber.filter(recipe_owner_id=id)

        if not follow.exists():
            return Response({'detail': 'Такой подписки нет'},
                            status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
