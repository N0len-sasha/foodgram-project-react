# Generated by Django 3.2.16 on 2023-12-05 08:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('unit', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('color_code', models.CharField(max_length=7, unique=True)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('image', models.ImageField(upload_to='images/')),
                ('description', models.TextField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user')),
                ('ingredient', models.ManyToManyField(related_name='ingredients', to='foodgram_api.Ingredient')),
                ('tag', models.ManyToManyField(related_name='tags', to='foodgram_api.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user')),
                ('follow', models.ManyToManyField(related_name='follows', to='users.User')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Favorites',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user')),
                ('recipe', models.ManyToManyField(related_name='favorites_recipes', to='foodgram_api.Recipe')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CheckList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user')),
                ('recipe', models.ManyToManyField(related_name='checklist_recipes', to='foodgram_api.Recipe')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
