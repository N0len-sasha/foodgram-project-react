from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.core.validators import MinValueValidator

from .models import (Tag, Ingredient, Favorites,
                     Recipe, CheckList, RecipeIngredient)
from users.models import FoodgramUser, Follow


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FoodgramUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return (
            'request' in self.context and
            self.context['request'].user.is_authenticated and
            Follow.objects.filter(author=self.context['request'].user,
                                  user_follow=obj).exists()
        )


class RelativeMediaURLField(serializers.ImageField):
    def to_representation(self, value):
        if not value:
            return None

        relative_path = super().to_representation(value)

        return f'/media/{relative_path}'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class GetIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.SlugField(
        source='ingredient.name', read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = RelativeMediaURLField(max_length=None, use_url=False)
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = GetIngredientSerializer(many=True,
                                          source='recipeingredient')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            'request' in self.context and
            user.is_authenticated and
            Favorites.objects.filter(author=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            'request' in self.context and
            user.is_authenticated and
            CheckList.objects.filter(author=user).exists()
        )


class CreateIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True,
                                      validators=[MinValueValidator(1)])

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=False,
                             allow_null=False, allow_empty_file=False)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = UserSerializer(read_only=True)
    ingredients = CreateIngredientSerializer(many=True, required=True)

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time']

    @staticmethod
    def create_ingredients(recipe, ingredients_data):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount'],
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Список тегов не может быть пустым.'
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Теги должны быть уникальными.')
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Список ингредиентов не может быть пустым.'
            )

        ingredient_ids = {el['id'] for el in value}

        if len(ingredient_ids) != len(value):
            raise serializers.ValidationError(
                'Дубликаты ингредиентов не разрешены.'
            )

        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        recipe.tags.set(tags_data)

        self.create_ingredients(recipe, ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        tags_data = validated_data.get('tags')

        instance.image = validated_data.get('image', instance.image)

        ingredients_data = validated_data.get('ingredients')
        instance.tags.set(tags_data)
        instance.ingredients.clear()
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['id']
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(recipe=instance,
                                            ingredient=ingredient,
                                            amount=amount)
        instance.save()

        return instance

    def to_representation(self, instance):
        recipe_serializer = RecipeSerializer(instance=instance,
                                             context=self.context)
        return recipe_serializer.data


class CheckListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckList
        fields = '__all__'


class RecipeReturnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowReturnSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = FoodgramUser
        fields = list(UserSerializer.Meta.fields) + ['recipes', 'recipes_count']

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
            except (ValueError, TypeError):
                recipes_limit = None
            recipes = recipes[:recipes_limit]
        return RecipeReturnSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        return (
            'request' in self.context and
            self.context['request'].user.is_authenticated and
            Follow.objects.filter(author=self.context['request'].user,
                                  user_follow=obj).exists()
        )
