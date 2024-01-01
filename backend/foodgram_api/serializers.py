from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField as DRF_Base64ImageField
from rest_framework import status

from .models import (Tag, Ingredient, Favorites,
                     Recipe, CheckList, RecipeIngredient)
from users.models import FoodgramUser, Follow
from .constants import MIN_INGREDIENT_VALUE


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FoodgramUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        if 'request' in self.context and self.context['request']:
            request = self.context['request']
            return (
                (
                    request.user.is_authenticated
                ) and (
                    request.user.subscriber.filter(recipe_owner=obj).exists()
                )
            )
        return False


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
    id = serializers.ReadOnlyField(source='ingredient_id')
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
        request = self.context['request']
        return (
            'request' in self.context and (
                request.user.is_authenticated
            ) and (
                request.user.favorites.filter(recipe=obj).exists()
            )
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        return (
            'request' in self.context and (
                request.user.is_authenticated
            ) and (
                request.user.checklist.filter(recipe=obj).exists()
            )
        )


class CreateIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True,
                                      min_value=MIN_INGREDIENT_VALUE)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


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
                {'detail': 'Список тегов не может быть пустым.'}
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                {'detail': 'Теги должны быть уникальными.'}
            )
        return value

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                {'detail': 'Поле image не может быть пустым'}
            )
        return value

    def validate(self, data):
        ingredients = data.get('ingredients', [])

        if not ingredients:
            raise serializers.ValidationError(
                {'detail': 'Список ингредиентов не может быть пустым.'}
            )

        ingredients_ids = [ingredient.get('id') for ingredient in ingredients]

        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(
                {'detail': 'Дубликаты ингредиентов не разрешены.'}
            )

        if 'tags' not in data:
            raise serializers.ValidationError(
                {'detail': 'Поле tags обязательно для обновления рецепта.'}
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
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        instance = super().update(instance, validated_data)

        instance.tags.set(tags_data)
        instance.ingredients.clear()
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['id']
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(recipe=instance,
                                            ingredient=ingredient,
                                            amount=amount)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance=instance,
                                context=self.context).data


class RecipeReturnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['subscriber', 'recipe_owner']

    def validate(self, data):
        recipe_owner_id = data.get('recipe_owner').id
        subscriber_id = data.get('subscriber').id
        user = self.context['request'].user

        if not user.is_authenticated:
            raise serializers.ValidationError(
                {'detail': 'Требуется авторизация'}
            )

        if recipe_owner_id == subscriber_id:
            raise serializers.ValidationError(
                {'detail': 'Нельзя подписаться на самого себя'}
            )

        if user.subscriber.filter(recipe_owner_id=recipe_owner_id).exists():
            raise serializers.ValidationError(
                {'detail': ('Подписка на пользователя c id'
                            f'{recipe_owner_id} уже существует')}
            )

        return data

    def to_representation(self, instance):
        recipes_limit = int(self.context['request'].query_params.get(
            'recipes_limit', 0)
        )

        return {
            **UserSerializer(instance.recipe_owner).data,
            'recipes': RecipeReturnSerializer(
                instance.recipe_owner.recipes.all()[:recipes_limit],
                many=True,
                context=self.context).data,
            'recipes_count': instance.recipe_owner.recipes.count(),
        }


class BaseRecipeActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = ['recipe', 'user']

    def validate(self, data):
        recipe_id = self.initial_data.get('recipe')
        user_id = self.initial_data.get('user')
        data['recipe'] = Recipe.objects.get(id=recipe_id)
        data['user'] = FoodgramUser.objects.get(id=user_id)
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError(
                {'detail': 'Требуется авторизация'},
                status=status.HTTP_401_UNAUTHORIZED)

        if not Recipe.objects.filter(id=recipe_id).exists():
            raise serializers.ValidationError(
                {'detail': f'Рецепт c id {recipe_id} не найден'}
            )
        if self.Meta.model.objects.filter(user_id=user_id,
                                          recipe_id=recipe_id).exists():
            raise serializers.ValidationError(
                ({'detail': f'Рецепт c id {recipe_id} уже'
                  'есть в {self.action_name}'})
            )
        return data

    def to_representation(self, instance):
        return RecipeReturnSerializer(
            Recipe.objects.get(id=instance.recipe_id)).data


class CheckListSerializer(BaseRecipeActionSerializer):
    class Meta(BaseRecipeActionSerializer.Meta):
        model = CheckList
        fields = ['recipe', 'user']

    action_name = 'чеклисте'


class FavoritesSerializer(BaseRecipeActionSerializer):
    class Meta(BaseRecipeActionSerializer.Meta):
        model = Favorites
        fields = ['recipe', 'user']

    action_name = 'избранном'


class ReturnRecipesCountSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

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
