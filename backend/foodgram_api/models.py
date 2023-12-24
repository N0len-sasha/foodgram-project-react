from django.db import models
from django.core.validators import (MinValueValidator,
                                    RegexValidator,
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
        validators=[RegexValidator(r'^[-a-zA-Z0-9_]+$',
                    'Wrong format')]
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
        unique_together = ['name', 'measurement_unit']

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
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    author = models.ForeignKey(
        FoodgramUser,
        null=True,
        on_delete=models.CASCADE,
        related_name='recipes'
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
        related_name='recipeingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipeingredient'
    )
    amount = models.IntegerField(
        validators=[
            MinValueValidator(MIN_INGREDIENT_VALUE,
                              message=INGREDIENT_VALIDATION_MESSAGE),
            MaxValueValidator(MAX_INGREDIENT_VALUE,
                              message=MAX_INGREDIENT_VALIDATION_MESSAGE)
        ]
    )


class BaseModel(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s'
    )
    user = models.ForeignKey(
        FoodgramUser,
        null=True,
        on_delete=models.CASCADE,
        related_name='%(class)s'
    )

    class Meta:
        abstract = True
        unique_together = ['user', 'recipe']


class CheckList(BaseModel):

    class Meta:
        verbose_name = 'Чеклист'
        verbose_name_plural = 'Чеклисты'

    def __str__(self):
        return f'Чеклист {self.pk}'


class Favorites(BaseModel):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'Favorites {self.pk}'