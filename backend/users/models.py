from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram_api.constants import (MAX_USER_CHARACTERS,
                                    MAX_EMAIL_CHARACTERS)
from .validators import validator_username


class FoodgramUser(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    username = models.CharField(
        'Логин',
        max_length=MAX_USER_CHARACTERS,
        unique=True,
        help_text=('Обязательное поле. Не более 150 символов. Только буквы,'
                   'цифры и символы @+-'),
        validators=(validator_username, ),
        error_messages={
            'unique': ('Пользователь с таким именем уже сущетсвует'),
        },
    )
    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
        max_length=MAX_EMAIL_CHARACTERS)
    first_name = models.CharField(
        'Имя',
        max_length=MAX_USER_CHARACTERS)
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_USER_CHARACTERS)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return self.username


class Follow(models.Model):
    recipe_owner = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='recipeauthor',
        verbose_name='Подписан на'
    )
    subscriber = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('subscriber', 'recipe_owner'),
                name='no_self_subscriptions'
            ),
            models.CheckConstraint(
                name='unique_subscriptions',
                check=~models.Q(subscriber=models.F('recipe_owner')),
            ),
        ]

    def __str__(self):
        return (f'Пользователь {self.subscriber.username}'
                f'подписан на {self.recipe_owner.username}')
