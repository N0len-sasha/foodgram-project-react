# Generated by Django 3.2.16 on 2023-12-14 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram_api', '0007_alter_recipe_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='follow',
            old_name='follow',
            new_name='user_follow',
        ),
    ]
