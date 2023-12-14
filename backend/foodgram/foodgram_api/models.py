from django.db import models
from django.core.validators import MinValueValidator

from users.models import CustomUser
from .constants import (MIN_INGREDIENT_VALUE,
                        INGREDIENT_VALIDATION_MESSAGE,
                        COOKING_VALIDATION_MESSAGE,
                        MIN_COOKING_VALUE,
                        MAX_NAME_LENGH,
                        MAX_HEX,
                        MAX_UNIT_LENGHT)


class BaseModel(models.Model):
    author = models.ForeignKey(CustomUser,
                               null=True,
                               on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Tag(models.Model):
    name = models.CharField('Название',
                            max_length=MAX_NAME_LENGH,
                            unique=True)
    color = models.CharField('Цвет(Hex)',
                             max_length=MAX_HEX,
                             unique=True)
    slug = models.SlugField(unique=True)


class Ingredient(models.Model):
    name = models.CharField('Название',
                            max_length=MAX_NAME_LENGH)
    measurement_unit = models.CharField('Мера',
                                        max_length=MAX_UNIT_LENGHT)


class Recipe(BaseModel):
    name = models.CharField('Название',
                            max_length=MAX_NAME_LENGH)
    image = models.ImageField('Изображение',
                              upload_to='images/', null=True)
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(MIN_COOKING_VALUE,
                              message=COOKING_VALIDATION_MESSAGE)
        ]
    )

    class Meta:
        ordering = ['name']


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipeingredient')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='recipeingredient')
    amount = models.IntegerField(
        validators=[
            MinValueValidator(MIN_INGREDIENT_VALUE,
                              message=INGREDIENT_VALIDATION_MESSAGE),
        ]
    )


class CheckList(BaseModel):
    recipe = models.ManyToManyField(
        Recipe,
        related_name='checklist_recipes'
    )


class Favorites(BaseModel):
    recipe = models.ManyToManyField(
        Recipe,
        related_name='favorites_recipes'
    )


class Follow(BaseModel):
    follow = models.ManyToManyField(
        CustomUser,
        related_name='follows'
    )
