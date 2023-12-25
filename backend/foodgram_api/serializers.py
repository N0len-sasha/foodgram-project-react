from django.shortcuts import get_object_or_404
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField as DRF_Base64ImageField
from django.core.validators import MinValueValidator
from rest_framework import status

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
            'request' in self.context and (
                self.context['request'].user.is_authenticated
            ) and (
                    Follow.objects.filter(user=self.context['request'].user,
                                          user_follow=obj).exists()
            )
        )


class Base64ImageField(DRF_Base64ImageField):

    def to_representation(self, image):
        return image.url


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
    image = Base64ImageField()
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
            'request' in self.context and (
                user.is_authenticated
            ) and (
                Favorites.objects.filter(user=user,
                                         recipe=obj).exists()
            )
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            'request' in self.context and (
                user.is_authenticated
            ) and (
                CheckList.objects.filter(user=user,
                                         recipe=obj).exists()
            )
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
    image = DRF_Base64ImageField(max_length=None,
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
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
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

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле image не может быть пустым'
            )
        return value

    def validate(self, data):
        ingredients = data.get('ingredients', [])

        if not ingredients:
            raise serializers.ValidationError(
                'Список ингредиентов не может быть пустым.'
            )

        seen_ids = set()
        unique_ingredients = []

        for el in ingredients:
            ingredient_id = el.get('id')

            if ingredient_id in seen_ids:
                raise serializers.ValidationError(
                    'Дубликаты ингредиентов не разрешены.'
                )

            seen_ids.add(ingredient_id)
            unique_ingredients.append(el)

        data['ingredients'] = unique_ingredients

        if 'tags' not in data:
            raise serializers.ValidationError(
                'Поле tags обязательно для обновления рецепта.'
            )

        return data

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


class RecipeReturnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowSerializer(serializers.Serializer):

    def create(self, validated_data):
        user_follow_id = validated_data.pop('user_follow_id')
        user_id = validated_data.pop('user')
        return Follow.objects.create(user_follow_id=user_follow_id,
                                     user_id=user_id)

    def validate(self, data):
        user_follow_id = self.initial_data.get('user_follow_id')
        user_id = self.initial_data.get('user')
        data['user_follow_id'] = user_follow_id
        data['user'] = user_id
        user = self.context['request'].user

        if not user.is_authenticated:
            raise serializers.ValidationError('Требуется авторизация')

        if int(user_follow_id) == user_id:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )

        get_object_or_404(FoodgramUser, id=user_follow_id)

        if Follow.objects.filter(user_id=user_id,
                                 user_follow_id=user_follow_id).exists():
            raise serializers.ValidationError(
                f'Рецепт c id {user_follow_id} уже есть в подписках'
            )
        return data

    def to_representation(self, instance):
        user_follow = FoodgramUser.objects.get(id=instance.user_follow_id)
        user_data = UserSerializer(user_follow).data
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        recipes = Recipe.objects.filter(author=user_follow)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        user_recipes_data = RecipeReturnSerializer(
            recipes, many=True,
            context=self.context
        ).data
        user_data['recipes'] = user_recipes_data
        user_data['recipes_count'] = recipes.count()

        return user_data


class CheckListSerializer(serializers.Serializer):

    def create(self, validated_data):
        recipe_id = validated_data.pop('recipe_id')
        user_id = validated_data.pop('user')
        return CheckList.objects.create(recipe_id=recipe_id,
                                        user_id=user_id)

    def validate(self, data):
        recipe_id = self.initial_data.get('recipe_id')
        user_id = self.initial_data.get('user')
        data['recipe_id'] = recipe_id
        data['user'] = user_id
        user = self.context['request'].user
        if not user.is_authenticated:
            return serializers.ValidationError(
                {'detail': 'Требуется авторизация'},
                status=status.HTTP_401_UNAUTHORIZED)
        try:
            Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            raise serializers.ValidationError(
                f'Рецепт c id {recipe_id} не найден'
            )
        if CheckList.objects.filter(user_id=user_id,
                                    recipe_id=recipe_id).exists():
            raise serializers.ValidationError(
                f'Рецепт c id {recipe_id} уже есть в чеклисте'
            )
        return data

    def to_representation(self, instance):
        recipe = Recipe.objects.get(id=instance.recipe_id)
        return RecipeReturnSerializer(recipe).data


class FavoritesSerializer(serializers.Serializer):

    def create(self, validated_data):
        recipe_id = validated_data.pop('recipe_id')
        user_id = validated_data.pop('user')
        return Favorites.objects.create(recipe_id=recipe_id,
                                        user_id=user_id)

    def validate(self, data):
        recipe_id = self.initial_data.get('recipe_id')
        user_id = self.initial_data.get('user')
        data['recipe_id'] = recipe_id
        data['user'] = user_id
        user = self.context['request'].user
        if not user.is_authenticated:
            return serializers.ValidationError(
                {'detail': 'Требуется авторизация'},
                status=status.HTTP_401_UNAUTHORIZED)
        try:
            Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            raise serializers.ValidationError(
                f'Рецепт c id {recipe_id} не найден'
            )
        if Favorites.objects.filter(user_id=user_id,
                                    recipe_id=recipe_id).exists():
            raise serializers.ValidationError(
                f'Рецепт c id {recipe_id} уже есть в избранном'
            )
        return data

    def to_representation(self, instance):
        recipe = Recipe.objects.get(id=instance.recipe_id)
        return RecipeReturnSerializer(recipe).data


class ReturnSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = FoodgramUser
        fields = list(UserSerializer.Meta.fields) + (
            ['recipes', 'recipes_count']
        )

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
            'request' in self.context and (
                self.context['request'].user.is_authenticated
            ) and (
                Follow.objects.filter(user=self.context['request'].user,
                                      user_follow=obj).exists()
            )
        )
