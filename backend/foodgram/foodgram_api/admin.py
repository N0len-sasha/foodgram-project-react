from django.contrib import admin

from .models import Tag, RecipeIngredient


@admin.register(Tag)
class Tag(admin.ModelAdmin):
    list_display = ['name', 'slug']


# @admin.register(RecipeIngredient)
# class Ingredient(admin.ModelAdmin):
#     list_display = ['name',]
