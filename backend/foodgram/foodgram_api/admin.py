from django.contrib import admin
from django.db import models

from .models import (Tag, RecipeIngredient, Ingredient,
                     CheckListRecipe, FavoritesRecipe, FollowUser,
                     Recipe, RecipeTag, CheckList, Favorites, Follow)
from users.models import CustomUser


class IngredientItemTabular(admin.TabularInline):
    model = RecipeIngredient


class TagItemTabular(admin.TabularInline):
    model = RecipeTag


class RecipeItemTabular(admin.TabularInline):
    model = CheckListRecipe


class RecipeFavoritesItemTabular(admin.TabularInline):
    model = FavoritesRecipe


class UserItemTabular(admin.TabularInline):
    model = FollowUser


@admin.register(Tag)
class Tag(admin.ModelAdmin):
    list_display = ['name', 'slug']


@admin.register(Ingredient)
class Ingredient(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    list_filter = ['name']


@admin.register(Recipe)
class Recipe(admin.ModelAdmin):
    list_display = ['name', 'author', 'favorites_count']

    list_filter = ['author', 'name', 'tags']

    inlines = [
        IngredientItemTabular,
        TagItemTabular
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            favorites_count=models.Count('favoritesrecipe')
        )

    def favorites_count(self, obj):
        return obj.favorites_count


@admin.register(CheckList)
class CheckList(admin.ModelAdmin):
    list_display = ['display_recipes', 'author']

    def display_recipes(self, obj):
        return ', '.join([recipe.name for recipe in obj.recipe.all()])

    display_recipes.short_description = 'Рецепты'

    inlines = [
        RecipeItemTabular,
    ]


@admin.register(Favorites)
class Favorites(admin.ModelAdmin):
    list_display = ['display_favorites', 'author']

    def display_favorites(self, obj):
        return ', '.join([recipe.name for recipe in obj.recipe.all()])

    display_favorites.short_description = 'Избранное'

    inlines = [
        RecipeFavoritesItemTabular,
    ]


@admin.register(Follow)
class Follow(admin.ModelAdmin):
    list_display = ['display_follow', 'author']

    def display_follow(self, obj):
        return ', '.join([user.first_name for user in obj.user_follow.all()])

    display_follow.short_description = 'Подписки'

    inlines = [
        UserItemTabular,
    ]


@admin.register(CustomUser)
class CustomUser(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role']

    list_filter = ['email', 'username']
