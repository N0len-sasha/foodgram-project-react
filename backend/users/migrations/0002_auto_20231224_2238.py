# Generated by Django 3.2.16 on 2023-12-24 19:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='foodgramuser',
            options={'ordering': ['id'], 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.RemoveField(
            model_name='follow',
            name='author',
        ),
    ]
