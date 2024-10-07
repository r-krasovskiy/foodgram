"""Модуль сериализаторов."""

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from foodgram.constants import MAX_LENGTH_MIDDLE
from foodgram.models import Favorite, Ingredient, Recipe, ShoppingList, Tag

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов"""
    model = Tag

    class Meta():
        fields = ('id', 'name', 'slug',)
        read_only_fields = '__all__'

class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели избранных рецептов."""

    name = serializers.ReadOnlyField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    coocking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)

    class Meta():
        model = Favorite
        fields = ('id', 'name', 'image', 'coocking_time')

class RrcipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецептов."""

    author = UserSerializer()
    tags = TagSerializer(many=True, read_only=True)

class ShoppingListSerializer(serializers.MOdelSerializer):
    """Сериализатор модели списка покупок."""
    name = serializers.ReadOnlyField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    coocking_time = serializers.IntegerField(source='recipe.cooking_time', read_only=True)
    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)

    class Meta():
        model = ShoppingList
        fields = ('id', 'name', 'image', 'coocking_time')

class IngredientSerializer(serializers.MOdelSerializer):
    """Сериализатор модели ингридиентов"""

    class Meta():
        model = Ingredient
        fields = ('id', 'name', 'amount')
        read_only_fields = '__all__'

class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецептов для чтения."""

    class Meta():
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')
        # read_only_fields = '__all__'

class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецептов для записи, редактирования, улдаления."""
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = AddIngredientSerializer(many=True, write_only=True)
    # author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_ingredients(self, ingredients):
        """Проверка, что """
        ingredients_data = [
            ingredient.get('id') for ingredient in ingredients
        ]
        if len(ingredients_data) != len(set(ingredients_data)):
            raise serializers.ValidationError(
                'Ингредиенты рецепта должны быть уникальными!'
            )
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть меньше 1'
                )
            if int(ingredient.get('amount')) > MAX_LENGTH_MIDDLE:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть больше 100'
                )
        return ingredients

    def validate_tags(self, tags):
        """Проверка, что введен хотя бы 1 тег добавлен в рецепт."""
        tags = tags
        if not tags:
            raise ValidationError(
                {'tags': 'Выберите по крайней мере один тег'})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError(
                    {'tags': 'Теги не должны повторяться'})
            tags_list.append(tag)
        return tags
