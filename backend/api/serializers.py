"""Модуль сериализаторов."""
import base64
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.files.base import ContentFile

from api.constants import (
    MAX_LENGTH_MIDDLE,
    MAX_LENGTH_LONG,
    MIN_COOKING_TIME,
    MAX_COOKING_TIME
)
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    ShoppingList,
    Tag,
    RecipeIngredient,
    Subscription
)

from djoser.serializers import UserCreateSerializer, UserSerializer


User = get_user_model()

class Base64ImageField(serializers.ImageField):
    """Для расшифровки изображений (рецепт, аватар)."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserPostSerializer(UserCreateSerializer):
    """Для содания пользователей."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'password', 'email')


class UserGetSerializer(UserSerializer):
    """Для изменения и отображения пользователей."""
    is_following = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_following', 'avatar')

    def validate(self, data):
        """Проверка нличия изображения."""
        if request := self.context.get('request'):
            if request.method == 'PUT' and not data:
                raise serializers.ValidationError('Выберите фото')
        return data

    def get_is_following(self, obj):
        """Проверка, подписан ли текущий юзер."""
        if request := self.context.get('request'):
            if request.user.is_anonymous:
                return False
            return request.user.following.filter(cooker=obj).exists()
        return False



class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов."""

    class Meta():
        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингридиентов."""

    class Meta():
        model = Ingredient
        fields = ('__all__')


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
        model = FavoriteRecipe
        fields = ('id', 'name', 'image', 'coocking_time')



class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецептов."""

    image = Base64ImageField(required=True, allow_null=False)
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор модели списка покупок."""
    name = serializers.ReadOnlyField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    coocking_time = serializers.IntegerField(source='recipe.cooking_time', read_only=True)
    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)

    class Meta():
        model = ShoppingList
        fields = ('id', 'name', 'image', 'coocking_time')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Ингредиент в рецепте -- используется при создании"""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        write_only=True,
        min_value=MAX_LENGTH_MIDDLE,
        max_value=MAX_LENGTH_LONG)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецептов для чтения."""

    author = UserGetSerializer()
    tags = TagSerializer(
        many=True,
    )
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta():
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image',
                  'tags', 'text', 'author', 'is_in_shopping_list'
        )
        read_only_fields = ('__all__',)

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipeingredient__amount')
        )
        return ingredients

    def get_is_recipe(self, obj, model):
        if request := self.context.get('request'):
            user = request.user
            if user.is_anonymous:
                return False
            return model.objects.filter(
                user=user, recipe=obj).exists()
        return False

    def get_is_favorited(self, obj):
        return self.get_is_recipe(obj, FavoriteRecipe)

    def get_is_in_shopping_cart(self, obj):
        return self.get_is_recipe(obj, ShoppingList)


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецептов для записи, редактирования, улдаления."""
 
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
        allow_null=False,
        allow_empty=False,
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True,
        allow_null=False,
        allow_empty=False,)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=True, allow_null=False)
    name = serializers.CharField(required=True, max_length=256)
    cooking_time = serializers.IntegerField(
        max_value=MAX_COOKING_TIME, min_value=MIN_COOKING_TIME)
    
    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time',
            'author')


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

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags_ingredients(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        recipe.tags.clear()
        recipe.ingredients.clear()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        self.add_tags_ingredients(recipe, tags, ingredients)
        recipe.save()
        return recipe


class FollowSerializer(serializers.Serializer):
    """Для валидации и создания подписки"""

    def validate(self, data):
        user = self.context['request'].user
        subs_id = self.context.get('user_pk')
        action = self.context.get('action')

        subs = get_object_or_404(User, pk=subs_id)
        if not subs:
            raise serializers.ValidationError('А на кого подписываемся?')
        if user == subs:
            raise serializers.ValidationError('На себя нельзя подписаться')

        following = user.following.filter(cooker=subs)
        if action == 'delete_subs':
            if not following:
                raise serializers.ValidationError('Такой подписки нет')
        if action == 'create_subs':
            if following:
                raise serializers.ValidationError('Подписка уже есть')
        return data

    def create(self, validated_data):
        limit_param = self.context.get('limit_param')
        subs = get_object_or_404(User, pk=validated_data.get('pk'))
        Follow.objects.create(
            user=self.context['request'].user,
            cooker=subs)
        return UserFollowSerializer(
            subs,
            context={'limit_param': limit_param})


class UserFollowSerializer(serializers.ModelSerializer):
    """Для подписки"""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_following = serializers.BooleanField(default=True)
    
    def get_recipes_count(self, obj):
            return obj.recipes.count()
    
    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        if limit_param := self.context.get('limit_param'):
            recipes = recipes[:int(limit_param)]
        serializer = RecipeReadSerializer(recipes, many=True, read_only=True)
        return serializer.data

    class Meta:
            model = User
            fields = (
                'id',
                'username',
                'first_name',
                'last_name',
                'email',
                'is_following',
                'avatar',
                'recipes_count',
                'recipes',
            )
