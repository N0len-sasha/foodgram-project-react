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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField('Название',
                            max_length=MAX_NAME_LENGH)
    measurement_unit = models.CharField('Мера',
                                        max_length=MAX_UNIT_LENGHT)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


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
        through='RecipeTag',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(MIN_COOKING_VALUE,
                              message=COOKING_VALIDATION_MESSAGE)
        ]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепты'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']


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


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipetag')
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            related_name='recipetag')


class CheckList(BaseModel):
    recipe = models.ManyToManyField(
        Recipe,
        through='CheckListRecipe',
        related_name='checklist_recipes'
    )

    class Meta:
        verbose_name = 'Чеклист'
        verbose_name_plural = 'Чеклисты'


class CheckListRecipe(models.Model):
    checklist = models.ForeignKey(CheckList,
                                  on_delete=models.CASCADE,
                                  related_name='checklistrecipe')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='checklistrecipe')


class Favorites(BaseModel):
    recipe = models.ManyToManyField(
        Recipe,
        through='FavoritesRecipe',
        related_name='favorites_recipes'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class FavoritesRecipe(models.Model):
    favorites = models.ForeignKey(Favorites,
                                  on_delete=models.CASCADE,
                                  related_name='favoritesrecipe')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favoritesrecipe')


class Follow(BaseModel):
    user_follow = models.ManyToManyField(
        CustomUser,
        through='FollowUser',
        related_name='follows'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class FollowUser(models.Model):
    follow = models.ForeignKey(Follow,
                               on_delete=models.CASCADE,
                               related_name='followuser')
    user_follow = models.ForeignKey(CustomUser,
                                    on_delete=models.CASCADE,
                                    related_name='followuser')
