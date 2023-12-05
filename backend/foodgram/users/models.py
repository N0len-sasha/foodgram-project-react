from django.db import models


class User (models.Model):
    login = models.CharField(max_length=50)
    password = models.CharField(max_length=15)
    email = models.EmailField(max_length=20)
    first_name = models.CharField(max_length=20)