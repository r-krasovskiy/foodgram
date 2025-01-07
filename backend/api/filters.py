"""Модуль для фильтрации поиска для API-запросов."""

from django.contrib.auth import get_user_model
from django_filters import FilterSet
from django_filters.rest_framework import filters
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class RecipeFilter(FilterSet):
    """Фильтрация рецептов."""

    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует избранные рецепты."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты по нахождению в списке покупок."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset

    def filter_by_tags(self, queryset, name, value):
        """Фильтрует рецепты по тегам."""
        tag_slugs = self.request.query_params.getlist('tags')
        if tag_slugs:
            return queryset.filter(tags__slug__in=tag_slugs).distinct()
        return queryset

    class Meta:
        """Метаданные фильтра."""

        model = Recipe
        fields = ('tags', 'author', 'is_in_shopping_cart')


class IngredientFilter(FilterSet):
    """Фильтрация ингредиентов по названию."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        """Метаданные фильтра."""

        model = Ingredient
        fields = ('name',)
