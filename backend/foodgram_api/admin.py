from django.contrib import admin
from django.db import models

from .models import (Tag, RecipeIngredient, Ingredient,
                     Recipe, CheckList, Favorites)


class IngredientItemTabular(admin.TabularInline):
    model = RecipeIngredient
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'
    min_num = 1


@admin.register(Tag)
class Tag(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')


@admin.register(Ingredient)
class Ingredient(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name', )


@admin.register(Recipe)
class Recipe(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count', 'display_ingredients')

    list_filter = ('author', 'name', 'tags')

    inlines = (
        IngredientItemTabular,
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            favorites_count=models.Count('favorites')
        )

    @admin.display(description='Ингредиенты')
    def display_ingredients(self, obj):
        return ', '.join(
            ingredient.name for ingredient in obj.ingredients.all()
        )

    @admin.display(description='Добавлено в избранное (кол-во)')
    def favorites_count(self, obj):
        return obj.favorites_count


@admin.register(CheckList)
class CheckList(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(Favorites)
class Favorites(admin.ModelAdmin):
    list_display = ('recipe', 'user')
