"""Модуль с моделями данных."""
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q

from api.constants import MAX_LENGTH_LONG, MAX_LENGTH_SHORT

User = get_user_model()


class Tag(models.Model):
    """Модель тегов к рецептам.

    Один рецепт может содержать несколько тегов.
    """

    name = models.CharField(
        verbose_name='Название тега',
        max_length=MAX_LENGTH_SHORT
    )
    slug = models.SlugField(
        verbose_name='Короткое имя (slug)',
        max_length=MAX_LENGTH_SHORT,
        unique=True,
        help_text='Укажите короткое имя (slug)'
    )

    class Meta():
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    """Модель ингридиентов рецептов."""

    name = models.CharField(
        verbose_name='Название ингридиента',
        max_length=MAX_LENGTH_LONG,
        help_text='Введите название ингридиента'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH_LONG,
        help_text='Введите единицы измерения'
    )

    class Meta():
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}'

class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        help_text='Автор рецепта'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=MAX_LENGTH_LONG,
        help_text='Введите название рецепта'
    )
    image = models.ImageField(
        verbose_name='Фото рецепта',
        upload_to='media/',
        help_text='Добавьте фото рецепта.'
    )
    text = models.TextField(
        verbose_name='Описани рецепта',
        help_text='Опишите процесс приготовления блюда.'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Укажите теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиент',
        help_text='Укажите ингридиенты блюда.'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1, 'Минимальное время приготовления, мин.')],
        help_text='Укажите время приговоления в минутах.'
    )
    pub_date = models.DateTimeField(
        'Дата публикации рецепта',
        auto_now_add=True,
    )

    class Meta():
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_recipe')]

    def __str__(self):
        return f'{self.name} - {self.author}'


class RecipeIngredient(models.Model):
    """Промежуточная модель связи ингридиентов с рецептами."""

    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients_recipe',
        verbose_name='Название блюда',
        on_delete=models.CASCADE,
        help_text='Выберите рецеп'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        help_text='Укажите ингредиенты'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, 'Должно быть указано не менее 1 ингридиента')],
        verbose_name='Количество ингридиента',
        help_text='Укажите количество'
    )

    class Meta():
        verbose_name = 'Ингридиенты рецепта'
        verbose_name_plural = 'Ингридиенты рецепта'
        constraints = [models.UniqueConstraint(
            fields=('recipe', 'ingredient'),
            name='unique_ingredients'
        )]

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class FavoriteRecipe(models.Model):
    """Рецепты, добавленные пользователями в избранное."""

    author = models.ForeignKey(
            User,
            related_name='favorite',
            on_delete=models.CASCADE,
            verbose_name='Автор рецепта',
            default=1)
    recipe = models.ForeignKey(
            Recipe,
            related_name='favorite',
            on_delete=models.CASCADE,
            verbose_name='Рецепты',
            default=1)

    class Meta:
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [models.UniqueConstraint(
            fields=['author', 'recipe'],
            name='unique_favorite')]

    def __str__(self):
        return f'{self.recipe}'


class ShoppingCart(models.Model):
    """Список покупок для приготовления рецепта."""

    user = models.ForeignKey(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        default=1)
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        verbose_name='Рецепт для приготовления',
        on_delete=models.CASCADE,
        help_text='Выберите рецепт для приготовления',
        default=1)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [models.UniqueConstraint(
            fields=['author', 'recipe'],
            name='unique_cart')]

    def __str__(self):
        return f'{self.recipe}'

    class Meta():
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Subscription(models.Model):
    """Подписки пользователя на авторов рецептов."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='following',
        on_delete=models.CASCADE,
        help_text='Текущий пользователь',
        default=1)
    author = models.ForeignKey(
        User,
        verbose_name='Подписка',
        related_name='followers',
        on_delete=models.CASCADE,
        help_text='Подписаться на автора рецепта',
        default=1)

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='no_self_following')]

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'

class RecipeTag(models.Model):
    """Тэги для рецептов."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт')
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE,
        verbose_name='Тег')

    class Meta:
        ordering = ('recipe', 'tag')
        verbose_name = 'тэг для рецепта'
        verbose_name_plural = 'Тэги для рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag'
            )
        ]

    def __str__(self):
        return f'На {self.tag} подойдёт {self.recipe}'
