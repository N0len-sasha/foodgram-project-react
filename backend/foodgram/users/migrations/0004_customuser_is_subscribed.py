# Generated by Django 3.2.16 on 2023-12-14 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_customuser_is_subscribed'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_subscribed',
            field=models.BooleanField(default=False),
        ),
    ]