from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters


from .models import Recipe


class CustomSearchFilter(SearchFilter):
    def filter_queryset(self, request, queryset, view):
        name = request.query_params.get('name', '')
        return queryset.filter(name__startswith=name) if name else queryset


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']
