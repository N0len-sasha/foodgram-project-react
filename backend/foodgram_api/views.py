import csv

from djoser.views import UserViewSet
from django.http import HttpResponse
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework import status, mixins, viewsets
from rest_framework.decorators import action


from .models import (Tag, Ingredient, Recipe,
                     CheckList, Favorites, RecipeIngredient)
from users.models import FoodgramUser, Follow
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          FollowSerializer,
                          ReturnSerializer,
                          UserSerializer,
                          FavoritesSerializer,
                          CreateRecipeSerializer,
                          CheckListSerializer)
from .pagination import PageNumberPagination
from .mixims import GetObjectMixim
from .permissions import IsAuthorOrReadOnly
from .filters import CustomSearchFilter, RecipeFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(GetObjectMixim):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [CustomSearchFilter, ]
    search_fields = ['^name', ]


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'ingredients').all()
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return CreateRecipeSerializer
        return RecipeSerializer

    @staticmethod
    def create_object(serializer_class, pk, request):
        create_data = {
            'user': request.user.id,
            'recipe_id': pk
        }
        context = {'request': request}
        serializer = serializer_class(data=create_data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_object(model, pk, request):
        try:
            Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response({'detail': 'Рецепт не существует'},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            obj = model.objects.get(recipe_id=pk, user=request.user)
        except model.DoesNotExist:
            return Response({'detail': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = ('attachment;'
                                           'filename="Ingredients.csv"')
        writer = csv.DictWriter(response, fieldnames=['Ингредиент',
                                                      'Количество',
                                                      'Мера'])
        writer.writeheader()

        writer.writerows([
            {'Ингредиент': ingredient['ingredient__name'],
             'Количество': ingredient['total_amount'],
             'Мера': ingredient['ingredient__measurement_unit']
             } for ingredient in ingredients
        ])

        return response


class SubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = FoodgramUser.objects.all()
    serializer_class = ReturnSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FoodgramUser.objects.filter(whofollow__user=self.request.user)


'''Пользователи'''


class CustomUserViewSet(UserViewSet):
    queryset = FoodgramUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        return FoodgramUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'me':
            return UserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated, ]
        return super().get_permissions()

    @action(detail=True, methods=['post'], url_path='subscribe')
    def follow(self, request, id):
        create_data = {
            'user': request.user.id,
            'user_follow_id': id
        }
        context = {'request': request}
        serializer = FollowSerializer(data=create_data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @follow.mapping.delete
    def delete_favorite(self, request, id):
        try:
            FoodgramUser.objects.get(id=id)
        except FoodgramUser.DoesNotExist:
            return Response({'detail': 'Пользователь не существует'},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            follow = Follow.objects.get(user_follow_id=id, user=request.user)
        except Follow.DoesNotExist:
            return Response({'detail': 'Такой подписки нет'},
                            status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
