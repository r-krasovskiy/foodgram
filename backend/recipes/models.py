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
        unique=True,
        max_length=MAX_LENGTH_SHORT,
        help_text='Укажите тег.'

    )
    slug = models.SlugField(
        verbose_name='Короткое имя (slug)',
        unique=True,
        max_length=MAX_LENGTH_SHORT,
        help_text='Укажите короткое имя (slug).'
    )

    class Meta():
        """Метаданные модели."""

        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Возвращает строковое представление тега."""
        return f'Тэг {self.name}'


class Ingredient(models.Model):
    """Модель ингридиентов рецептов."""

    name = models.CharField(
        verbose_name='Название ингридиента',
        unique=True,
        max_length=MAX_LENGTH_LONG,
        help_text='Введите название ингридиента.'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH_SHORT,
        help_text='Введите единицы измерения.'
    )

    class Meta():
        """Метаданные модели."""

        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        """Возвращает строковое представление ингридиента."""
        return f'Ингридиент {self.name}'


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Автор рецепта (добавляется автоматически).'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=MAX_LENGTH_LONG,
        help_text='Введите название рецепта.'
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
        validators=[MinValueValidator(
            1,
            'Минимальное время приготовления, мин.')
        ],
        help_text='Укажите время приготовления в минутах.'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True,
    )

    class Meta():
        """Метаданные модели."""

        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """Возвращает строковое представление рецепта."""
        return f'Рецепт {self.name} от автора {self.author}'


class RecipeIngredient(models.Model):
    """Промежуточная модель связи ингридиентов с рецептами."""

    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients_recipe',
        verbose_name='Название блюда',
        on_delete=models.CASCADE,
        help_text='Выберите рецепт.'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        help_text='Укажите ингредиенты'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                'Должно быть указано не менее 1 ингридиента')
        ],
        verbose_name='Количество ингридиента',
        help_text='Укажите количество.'
    )

    class Meta():
        """Метаданные модели."""

        verbose_name = 'Ингридиенты рецепта'
        verbose_name_plural = 'Ингридиенты рецепта'
        constraints = [models.UniqueConstraint(
            fields=('recipe', 'ingredient'),
            name='unique_ingredients'
        )]

    def __str__(self):
        """Возвращает строковое представление ингридиента."""
        return f'Ингридиент {self.ingredient} в количестве {self.amount}'


class FavoriteRecipe(models.Model):
    """Рецепты, добавленные пользователями в избранное."""

    user = models.ForeignKey(
        User,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Рецепты'
    )

    class Meta:
        """Метаданные модели."""

        ordering = ('user', 'recipe')
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        """Возвращает строковое представление рецепта в избранном."""
        return f'Рецепт {self.recipe} в избранном у пользователя {self.user}'


class ShoppingCart(models.Model):
    """Список покупок для приготовления рецепта."""

    user = models.ForeignKey(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        verbose_name='Рецепт для приготовления',
        on_delete=models.CASCADE,
        help_text='Выберите рецепт для приготовления',
    )

    class Meta:
        """Метаданные модели."""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        """Возвращает строковое представление рецепта в списке."""
        return f'Рецепт {self.recipe} в списке {self.user}'


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
        """Метаданные модели."""

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
        """Возвращает строковое представление подписки."""
        return f'Пользователь {self.user} подписан на {self.author}'


class RecipeTag(models.Model):
    """Тэги для рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег')

    class Meta:
        """Метаданные модели."""

        ordering = ('recipe', 'tag')
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag'
            )
        ]

    def __str__(self):
        """Возвращает строковое представление тега."""
        return f'Тэг {self.tag} для рецепта {self.recipe}'
