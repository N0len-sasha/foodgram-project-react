# Generated by Django 3.2.16 on 2024-01-09 09:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='foodgramuser',
            options={'ordering': ('first_name', 'last_name'), 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
    ]