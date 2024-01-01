import csv
import tempfile

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
from .filters import CustomSearchFilter, RecipeFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (CustomSearchFilter, )
    search_fields = ['^name', ]


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'ingredients').all()
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
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
        if not Recipe.objects.filter(id=pk).exists():
            return Response({'detail': 'Рецепт не существует'},
                            status=status.HTTP_404_NOT_FOUND)

        obj = model.objects.filter(recipe_id=pk, user=request.user)
        if not obj.exists():
            return Response({'detail': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def write_csv_data(ingredients, file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Ингредиент', 'Количество', 'Мера'])

            for ingredient in ingredients:
                writer.writerow([
                    ingredient['ingredient__name'],
                    ingredient['total_amount'],
                    ingredient['ingredient__measurement_unit']
                ])

    @action(detail=True, methods=['post'], url_path='favorite')
    def favorite(self, request, pk):
        return self.create_object(FavoritesSerializer, pk, request)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_object(Favorites, pk, request)

    @action(detail=True, methods=['post'], url_path='shopping_cart')
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

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.write_csv_data(ingredients, temp_file.name)

        response = FileResponse(open(temp_file.name, 'rb'),
                                as_attachment=True,
                                filename='Ingredients.csv')
        temp_file.close()

        return response


'''Пользователи'''


class CustomUserViewSet(UserViewSet):
    queryset = FoodgramUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=['post'], url_path='subscribe')
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

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscribtions(self, request):
        queryset = FoodgramUser.objects.filter(
            subscriber__subscriber=self.request.user
        )
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ReturnRecipesCountSerializer(result_page,
                                                  many=True,
                                                  context={'request': request})

        return paginator.get_paginated_response(serializer.data)

    @follow.mapping.delete
    def delete_subscribtions(self, request, id):
        if not FoodgramUser.objects.filter(id=id).exists():
            return Response({'detail': 'Пользователь не существует'},
                            status=status.HTTP_404_NOT_FOUND)

        follow = request.user.subscriber.filter(recipe_owner_id=id)
        if not follow:
            return Response({'detail': 'Такой подписки нет'},
                            status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
