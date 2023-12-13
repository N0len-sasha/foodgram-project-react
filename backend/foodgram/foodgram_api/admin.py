from django.contrib import admin

from .models import Tag, RecipeIngredient
from users.models import CustomUser


@admin.register(Tag)
class Tag(admin.ModelAdmin):
    list_display = ['name', 'slug']


@admin.register(CustomUser)
class CustomUser(admin.ModelAdmin):
    list_display = ['username', 'role']
