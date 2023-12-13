import base64
from rest_framework import serializers
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer, UserCreateSerializer

from .models import (Tag, Ingredient, Recipe, CheckList, Favorites, Follow, RecipeIngredient)
from users.models import CustomUser

'''Пользователи'''


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('email', 'id', 'username', 'password',
                  'first_name', 'last_name')


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')


'''Словари'''


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr),
                               name=f'uploaded_image.{ext}')

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


'''Рецепты'''


class GetIngredientSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = CustomUserSerializer(read_only=True)
    ingredients = GetIngredientSerializer(many=True,
                                          source='recipeingredient')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time']

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.favorites_recipes.filter(author=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.checklist_recipes.filter(author=user).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        tags_data = TagSerializer(
            Tag.objects.filter(id__in=representation['tags']),
            many=True).data
        representation['tags'] = tags_data
        return representation


class CreateIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = CustomUserSerializer(read_only=True)
    ingredients = CreateIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart']

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.favorites_recipes.filter(author=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.checklist_recipes.filter(author=user).exists()
        return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        for ingredients_data in ingredients_data:
            ingredient = ingredients_data['id']
            amount = ingredients_data['amount']
            RecipeIngredient.objects.create(recipe=recipe,
                                            ingredient=ingredient,
                                            amount=amount)

        return recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        tags_data = TagSerializer(Tag.objects.filter(
            id__in=representation['tags']), many=True).data
        representation['tags'] = tags_data

        recipe = Recipe.objects.get(id=representation['id'])
        ingredients_data = RecipeIngredient.objects.filter(recipe=recipe)
        ingredient_data = GetIngredientSerializer(
            ingredients_data, many=True).data
        representation['ingredients'] = ingredient_data

        return representation


'''Сборники'''


class CheckListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckList
        fields = '__all__'


class FavoritesSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Favorites
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'
