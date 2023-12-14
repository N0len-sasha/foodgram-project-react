from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram_api.constants import (USER,
                                    ADMIN,
                                    AUTH_USER,
                                    MAX_USER_CHARACTERS,
                                    MAX_EMAIL_CHARACTERS)
from .validators import validator_username

ROLE_CHOICES = [
        (USER, 'Гость'),
        (AUTH_USER, 'Авторизованный пользователь'),
        (ADMIN, 'Администратор'),
    ]


class CustomUser(AbstractUser):
    username = models.CharField(
        'Логин',
        max_length=MAX_USER_CHARACTERS,
        unique=True,
        help_text=('Обязательное поле. Не более 150 символов. Только буквы,'
                   'цифры и символы @+-'),
        validators=[validator_username],
        error_messages={
            'unique': ("Пользователь с таким именем уже сущетсвует"),
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
    is_subscribed = models.BooleanField(default=False)
    role = models.CharField(
        max_length=max(len(choice[0]) for choice in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Уровень доступа'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
