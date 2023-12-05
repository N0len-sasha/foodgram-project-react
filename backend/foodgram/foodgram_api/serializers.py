from rest_framework import serializers

from .models import (Tag, Ingredient, Recipe, CheckList, Favorites, Follow)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'


class CheckListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckList
        fields = '__all__'


class FavoritesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorites
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'
