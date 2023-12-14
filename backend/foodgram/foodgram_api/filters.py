from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters

from .models import Recipe


class CustomSearchFilter(SearchFilter):
    def get_search_terms(self, request):
        return request.query_params.get('name', '')


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='tags__slug',
                              lookup_expr='icontains',
                              label='Tags')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']
