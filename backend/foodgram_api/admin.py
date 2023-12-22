from django.contrib import admin
from django.db import models

from .models import (Tag, RecipeIngredient, Ingredient,
                     Recipe, CheckList, Favorites)


class IngredientItemTabular(admin.TabularInline):
    model = RecipeIngredient

    def get_min_num(self, request, obj=None, **kwargs):
        return 1


@admin.register(Tag)
class Tag(admin.ModelAdmin):
    list_display = ('name', 'slug')


@admin.register(Ingredient)
class Ingredient(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ['name']


@admin.register(Recipe)
class Recipe(admin.ModelAdmin):
    list_display = ['name', 'author', 'favorites_count', 'display_ingredients']

    list_filter = ['author', 'name', 'tags']

    inlines = [
        IngredientItemTabular,
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            favorites_count=models.Count('favoritesrecipe')
        )

    @admin.display(description='Ингредиенты')
    def display_ingredients(self, obj):
        ingredients = obj.ingredients.all()
        return ', '.join(str(ingredient) for ingredient in ingredients)

    @admin.display(description='Добавлено в избранное (кол-во)')
    def favorites_count(self, obj):
        return obj.favorites_count


@admin.register(CheckList)
class CheckList(admin.ModelAdmin):
    list_display = ['display_recipes', 'author']

    @admin.display(description='Рецепты')
    def display_recipes(self, obj):
        return ', '.join([recipe.name for recipe in obj.recipe.all()])

    display_recipes.short_description = 'Рецепты'


@admin.register(Favorites)
class Favorites(admin.ModelAdmin):
    list_display = ['display_favorites', 'author']

    @admin.display(description='Избранное')
    def display_favorites(self, obj):
        return ', '.join([recipe.name for recipe in obj.recipe.all()])

    display_favorites.short_description = 'Избранное'
