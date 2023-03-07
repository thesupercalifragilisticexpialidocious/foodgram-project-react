# Generated by Django 2.2.19 on 2023-03-07 14:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'избранное',
                'verbose_name_plural': 'избранные',
                'ordering': ('user', 'recipe'),
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='название')),
                ('unit', models.CharField(choices=[('G', 'г'), ('KG', 'кг'), ('ML', 'мл'), ('L', 'л'), ('TSP', 'ч. л.'), ('TBSP', 'ст. л.'), ('PC', 'шт.'), ('AD_LIB', 'по вкусу'), ('GLASS', 'стакан'), ('DROP', 'капля'), ('HANDFUL', 'горсть'), ('SLICE', 'кусок'), ('PACK', 'пакет'), ('BUNCH', 'пучок'), ('PINCH', 'щепотка'), ('CAN', 'банка'), ('PACKAGE', 'упаковка'), ('STAR', 'звездочка'), ('SEGMENT', 'долька'), ('CLOVE', 'зубчик'), ('LAYER', 'пласт'), ('CARCASS', 'тушка'), ('POD', 'стручок'), ('BRANCH', 'веточка'), ('BTL', 'бутылка'), ('LOAF', 'батон'), ('BAG', 'пакетик'), ('LEAF', 'лист'), ('STEM', 'стебель')], max_length=16, verbose_name='ед. измерения')),
            ],
            options={
                'verbose_name': 'ингредиент',
                'verbose_name_plural': 'ингредиенты',
                'ordering': ('name',),
                'default_related_name': 'ingredient',
            },
        ),
        migrations.CreateModel(
            name='IngredientPerRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Укажите число не менее 1'), django.core.validators.MaxValueValidator(8000, message='Укажите число до 8000')], verbose_name='количество')),
            ],
            options={
                'verbose_name': 'ингридиент на блюдо',
                'verbose_name_plural': 'ингридиенты на блюда',
                'ordering': ('recipe', 'ingredient'),
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, verbose_name='название')),
                ('description', models.TextField(max_length=4096, unique=True, verbose_name='описание')),
                ('cooking_time', models.DurationField(verbose_name='время приготовления')),
                ('image', models.ImageField(unique=True, upload_to='recipes/', verbose_name='фото')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='дата и время опубликования')),
            ],
            options={
                'verbose_name': 'рецепт',
                'verbose_name_plural': 'рецепты',
                'ordering': ('-pub_date',),
                'default_related_name': 'recipe',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='название')),
                ('color', models.PositiveIntegerField(unique=True, validators=[django.core.validators.MaxValueValidator(16777215, message='Максимльное значение - FFFFFF')])),
                ('slug', models.SlugField(max_length=16, unique=True, verbose_name='слаг')),
            ],
            options={
                'verbose_name': 'тэг',
                'verbose_name_plural': 'тэги',
                'ordering': ('name',),
                'default_related_name': 'tag',
            },
        ),
    ]
