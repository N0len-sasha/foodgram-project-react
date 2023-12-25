from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

from .models import FoodgramUser, Follow


@admin.register(Follow)
class Follow(admin.ModelAdmin):
    list_display = ['user_follow', 'user']


@admin.register(FoodgramUser)
class CustomUser(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'get_followers', 'get_recipes')

    list_filter = ['email', 'username']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipes_count=Count('recipes'),
            followers_count=Count('follower'),
        )

    @admin.display(description='Подписчики')
    def get_followers(self, obj):
        return obj.followers_count

    @admin.display(description='Созданные рецепты')
    def get_recipes(self, obj):
        return obj.recipes_count
