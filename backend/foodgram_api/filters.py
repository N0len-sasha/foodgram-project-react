from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters

from .models import Recipe


class IngredientSearchFilter(SearchFilter):
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
        fields = ('author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user.id)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(checklist__user=self.request.user.id)
        return queryset
