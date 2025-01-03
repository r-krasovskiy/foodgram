# Generated by Django 4.2.16 on 2025-01-02 15:01

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favoriterecipe',
            options={'ordering': ('user', 'recipe'), 'verbose_name': 'Избранные рецепты', 'verbose_name_plural': 'Избранные рецепты'},
        ),
        migrations.AlterModelOptions(
            name='recipetag',
            options={'ordering': ('recipe', 'tag'), 'verbose_name': 'Тег рецепта', 'verbose_name_plural': 'Теги рецепта'},
        ),
        migrations.RemoveConstraint(
            model_name='favoriterecipe',
            name='unique_favorite',
        ),
        migrations.RemoveConstraint(
            model_name='recipe',
            name='unique_recipe',
        ),
        migrations.RemoveConstraint(
            model_name='shoppingcart',
            name='unique_cart',
        ),
        migrations.RemoveField(
            model_name='favoriterecipe',
            name='author',
        ),
        migrations.AddField(
            model_name='favoriterecipe',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='favoriterecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to='recipes.recipe', verbose_name='Рецепты'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(help_text='Введите единицы измерения.', max_length=20, verbose_name='Единица измерения'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(help_text='Введите название ингридиента.', max_length=200, unique=True, verbose_name='Название ингридиента'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(help_text='Автор рецепта (добавляется автоматически).', on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(help_text='Введите название рецепта.', max_length=200, verbose_name='Название рецепта'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(help_text='Укажите количество.', validators=[django.core.validators.MinValueValidator(1, 'Должно быть указано не менее 1 ингридиента')], verbose_name='Количество ингридиента'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(help_text='Выберите рецепт.', on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_recipe', to='recipes.recipe', verbose_name='Название блюда'),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='recipe',
            field=models.ForeignKey(help_text='Выберите рецепт для приготовления', on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to='recipes.recipe', verbose_name='Рецепт для приготовления'),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(help_text='Укажите тег.', max_length=20, unique=True, verbose_name='Название тега'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(help_text='Укажите короткое имя (slug).', max_length=20, unique=True, verbose_name='Короткое имя (slug)'),
        ),
    ]
