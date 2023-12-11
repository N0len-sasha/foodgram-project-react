from django.db import models
from django.core.validators import MinValueValidator

from users.models import CustomUser
from .constants import (MIN_INGREDIENT_VALUE,
                        INGREDIENT_VALIDATION_MESSAGE,
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
    color_code = models.CharField('Цвет(Hex)',
                                  max_length=MAX_HEX,
                                  unique=True)
    slug = models.SlugField(unique=True)


class Ingredient(models.Model):
    name = models.CharField('Название',
                            max_length=MAX_NAME_LENGH)
    measurement_unit = models.CharField('Мера',
                                        max_length=MAX_UNIT_LENGHT)


class Recipe(BaseModel):
    name = models.CharField(max_length=MAX_NAME_LENGH)
    image = models.ImageField(upload_to='images/', null=True)
    text = models.TextField()
    ingredient = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='ingredients'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags'
    )
    cooking_time = models.IntegerField


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
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
