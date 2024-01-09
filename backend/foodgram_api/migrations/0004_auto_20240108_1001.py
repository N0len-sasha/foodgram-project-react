# Generated by Django 3.2.16 on 2024-01-08 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram_api', '0003_alter_recipeingredient_amount'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='checklist',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='checklist_user_recipe_unique'),
        ),
        migrations.AddConstraint(
            model_name='favorites',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='favorites_user_recipe_unique'),
        ),
    ]