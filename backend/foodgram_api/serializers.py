import base64
from rest_framework import serializers
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer, UserCreateSerializer


from .models import (Follow, Tag, Ingredient,
                     Recipe, CheckList, RecipeIngredient)
from users.models import CustomUser


'''Пользователи'''


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('email', 'id', 'username', 'password',
                  'first_name', 'last_name')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Follow.objects.filter(author=user, user_follow=obj).exists()
        return False


'''Словари'''


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr),
                               name=f'uploaded_image.{ext}')

        return super().to_internal_value(data)


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
    image = RelativeMediaURLField(max_length=None, use_url=False)
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

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Убедитесь, что это значение больше либо равно 1.'
            )
        return value


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=False)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = CustomUserSerializer(read_only=True)
    ingredients = CreateIngredientSerializer(many=True, required=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart']

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
        ingredient_ids = set()
        for el in value:
            if not el:
                raise serializers.ValidationError(
                    'Ингредиент не может быть пустым.'
                )
            ingredient_id = el['id']
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    'Дубликаты ингредиентов не разрешены.'
                )
            ingredient_ids.add(ingredient_id)
        return value

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

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        tags_data = validated_data.get('tags')

        instance.image = validated_data.get('image', instance.image)

        ingredients_data = validated_data.get('ingredients')

        if not tags_data or not ingredients_data:
            raise serializers.ValidationError(
                'Список тегов или ингредиентов не может быть пустым.'
            )

        if tags_data:
            instance.tags.set(tags_data)

        if ingredients_data:
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


class RecipeReturnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowReturnSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', ]

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        recipes = Recipe.objects.filter(author=obj)
        if recipes_limit is not None:
            recipes_queryset = recipes[:int(recipes_limit)]
            return RecipeReturnSerializer(recipes_queryset, many=True).data
        return RecipeReturnSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
