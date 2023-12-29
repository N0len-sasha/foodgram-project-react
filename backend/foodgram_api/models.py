from django.db import models
from django.core.validators import (MinValueValidator,
                                    MaxValueValidator)
from colorfield.fields import ColorField

from users.models import FoodgramUser
from .constants import (MIN_INGREDIENT_VALUE,
                        INGREDIENT_VALIDATION_MESSAGE,
                        COOKING_VALIDATION_MESSAGE,
                        MIN_COOKING_VALUE,
                        MAX_NAME_LENGH,
                        MAX_COOKING_VALUE,
                        MAX_COOKING_VALIDATION_MESSAGE,
                        MAX_INGREDIENT_VALUE,
                        MAX_INGREDIENT_VALIDATION_MESSAGE)


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=MAX_NAME_LENGH,
        unique=True
    )
    color = ColorField(
        'Цвет(Hex)'
    )
    slug = models.SlugField(
        unique=True,
        max_length=MAX_NAME_LENGH,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=MAX_NAME_LENGH
    )
    measurement_unit = models.CharField(
        'Мера',
        max_length=MAX_NAME_LENGH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient_fields'
            ),
        )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        'Название',
        max_length=MAX_NAME_LENGH
    )
    image = models.ImageField(
        'Изображение',
        upload_to='images/'
    )
    text = models.TextField(
        'Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег'
    )
    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=(
            MinValueValidator(MIN_COOKING_VALUE,
                              message=COOKING_VALIDATION_MESSAGE),
            MaxValueValidator(MAX_COOKING_VALUE,
                              message=MAX_COOKING_VALIDATION_MESSAGE)
        )
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепты'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredient',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipeingredient',
        verbose_name='Ингредиент'
    )
    amount = models.SmallIntegerField(
        validators=[
            MinValueValidator(MIN_INGREDIENT_VALUE,
                              message=INGREDIENT_VALIDATION_MESSAGE),
            MaxValueValidator(MAX_INGREDIENT_VALUE,
                              message=MAX_INGREDIENT_VALIDATION_MESSAGE)
        ]
    )


class RecipeUserModel(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        FoodgramUser,
        null=True,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Пользователь'
    )

    class Meta:
        abstract = True
        unique_together = ['user', 'recipe']


class CheckList(RecipeUserModel):

    class Meta:
        verbose_name = 'Чеклист'
        verbose_name_plural = 'Чеклисты'

    def __str__(self):
        return f'Чеклист {self.pk}'


class Favorites(RecipeUserModel):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'Избранное {self.pk}'
