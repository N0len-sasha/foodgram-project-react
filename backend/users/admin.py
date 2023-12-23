from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

from .models import FoodgramUser, Follow


@admin.register(Follow)
class Follow(admin.ModelAdmin):
    list_display = ['display_follow', 'author']

    @admin.display(description='Подписки')
    def display_follow(self, obj):
        return ', '.join([user.first_name for user in obj.user_follow.all()])

    display_follow.short_description = 'Подписки'


@admin.register(FoodgramUser)
class CustomUser(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'get_followers', 'get_recipes')

    list_filter = ['email', 'username']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipes_count=Count('recipe'),
        )

    @admin.display(description='Подписчики')
    def get_followers(self, obj):
        return obj.followuser.count()

    @admin.display(description='Созданные рецепты')
    def get_recipes(self, obj):
        return obj.recipes_count
