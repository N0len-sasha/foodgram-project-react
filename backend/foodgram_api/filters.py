from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters


from .models import Recipe, CheckList, Favorites


class CustomSearchFilter(SearchFilter):
    def filter_queryset(self, request, queryset, view):
        name = request.query_params.get('name', '')
        return queryset.filter(name__startswith=name) if name else queryset


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_in_shopping_cart = filters.Filter(
        method='filter_is_in_shopping_cart',
        label='В чеклисте'
    )
    is_favorited = filters.Filter(
        method='filter_is_favorited',
        label='В избранном'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        is_favorited = self.request.query_params.get(
            'is_favorited'
        )
        if is_favorited is not None and int(
            is_favorited) == 1 and (
                self.request.user.is_authenticated):
            try:
                favorites_id = self.request.user.favorites.all().values(
                    'recipe_id'
                )
                return Recipe.objects.filter(id__in=favorites_id)
            except Favorites.DoesNotExist:
                return Recipe.objects.none()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_in_shopping_cart is not None and int(
            is_in_shopping_cart) == 1 and (
                self.request.user.is_authenticated):
            try:
                checklist_id = self.request.user.checklist.all().values(
                    'recipe_id'
                )
                return Recipe.objects.filter(id__in=checklist_id)
            except CheckList.DoesNotExist:
                return Recipe.objects.none()
        return queryset
