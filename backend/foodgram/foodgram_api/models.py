from django.db import models

from users.models import User


class BaseModel(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Tag(models.Model):
    name = models.CharField(max_length=256, unique=True)
    color_code = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(unique=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=256)
    count = models.IntegerField
    unit = models.CharField(max_length=20)


class Recipe(BaseModel):
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='images/')
    description = models.TextField()
    ingredient = models.ManyToManyField(
        Ingredient,
        related_name='ingredients'
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='tags'
    )
    time = models.IntegerField


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
        User,
        related_name='follows'
    )
