"""Модуль с моделями данных."""
from django.db import models
from django.db.models import Q, F
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from api.constants import MAX_LENGTH_SHORT, MAX_LENGTH_LONG

User = get_user_model()


class Tag(models.Model):
    """Модель тегов к рецептам.

    Один рецепт может содержать несколько тегов.
    """

    name = models.CharField(
        verbose_name='',
        max_length=MAX_LENGTH_SHORT
    )
    slug = models.SlugField(
        verbose_name='Короткое имя (slug)',
        max_length=MAX_LENGTH_SHORT,
        unique=True,
        help_text='Укажите короткое имя (slug)'
    )

    class Meta():
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
    measure = models.CharField(
        verbose_name='',
        max_length=MAX_LENGTH_LONG,
        help_text='Введите единицы измерения'       
    )

    class Meta():
        ordering = ['id']
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
    picture = models.ImageField(
        verbose_name='Фото рецепта',
        upload_to='media/',
        help_text='Добавьте фото рецепта.'
    )
    description = models.TextField(
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
        through='IngredientRecipe',
        verbose_name='Ингредиент',
        help_text='Укажите ингридиенты блюда.'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='',
        validators=[MinValueValidator(1, 'Минимальное время приготовления, мин.')],
        help_text='Укажите время приговоления блюда в минутах.'
    )

    class Meta():
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe')]


class IngredientRecipe(models.Model):
    """Промежуточная модель связи ингридиентов в рецептах."""

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
        verbose_name='Количество',
        help_text='Укажите количество'
    )

    class Meta():
        verbose_name = 'Ингридиенты рецепта'
        verbose_name_plural = 'Ингридиенты рецепта'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_ingredients'
        )]

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Favorite(models.Model):
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

    class Meta():
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingList(models.Model):

    """Список покупок для приготовления рецепта."""
    author = models.ForeignKey(
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
        related_name='follower',
        on_delete=models.CASCADE,
        help_text='Текущий пользователь',
        default=1)
    author = models.ForeignKey(
        User,
        verbose_name='Подписка',
        related_name='followed',
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
