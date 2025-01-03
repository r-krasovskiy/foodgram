"""Модуль сериализаторов API."""

import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.db.models import F, Q
from django.shortcuts import get_list_or_404, get_object_or_404

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from api.constants import (
    MAX_COOKING_TIME,
    MAX_INGREDIENTS,
    MAX_LENGTH_MIDDLE,
    MIN_COOKING_TIME,
    MIN_INGREDIENTS,
)
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingCart,
    Subscription,
    Tag,
)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Декодирование изображений, переданных в формате Base64."""

    def to_internal_value(self, data):
        """Преобразует входные данные в объект изображения."""
        if isinstance(data, str) and data.startswith('data:image'):
            try:
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(
                    base64.b64decode(imgstr),
                    name=f'temp.{ext}'
                )
            except (ValueError, IndexError, base64.binascii.Error) as error:
                raise serializers.ValidationError(
                    'Неверный формат Base64 изображения!'
                ) from error
        return super().to_internal_value(data)


class UserPostSerializer(UserCreateSerializer):
    """Сериализатор для создания нового пользователя через API."""

    username = serializers.CharField(
        max_length=MAX_LENGTH_MIDDLE,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=(
                    'Имя пользователя может содержать только буквы, цифры '
                    'и символы @/./+/-/_'
                )
            )
        ]
    )

    class Meta(UserCreateSerializer.Meta):
        """Метаданные сериализатора."""

        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'password'
        )


class UserGetSerializer(UserSerializer):
    """Сериализатор для получения информации о пользователе через API."""

    is_subscribed = serializers.SerializerMethodField(
        help_text='Показывает, подписан ли текущий пользователь на данного.'
    )
    avatar = Base64ImageField(
        required=False,
        allow_null=True,
        help_text='Аватар пользователя.'
    )

    class Meta:
        """Метаданные сериализатора."""

        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def validate(self, data):
        """Валидирует наличие аватара при обновлении."""
        request = self.context.get('request')
        if request and request.method == 'PUT':
            if not data.get('avatar'):
                raise serializers.ValidationError('Выберите фото для аватара!')
        return data

    def get_is_subscribed(self, obj):
        """Определяет, подписан ли текущий пользователь на данного."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(user=request.user).exists()
        return False

    def get_avatar(self, obj):
        """Возвращает абсолютный URL аватара пользователя."""
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        """Метаданные сериализатора."""

        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор инргедиентов."""

    class Meta:
        """Метаданные сериализатора."""

        model = Ingredient
        fields = ('__all__')


class RecipeGetSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения информации о рецептах через API.

    Включает информацию о:
    - Авторе рецепта.
    - Тегах, связанных с рецептом.
    - Ингредиентах и их количестве.
    - Наличии рецепта в избранном и в корзине покупок.
    """

    author = UserGetSerializer(help_text="Информация об авторе рецепта.")
    tags = TagSerializer(
        many=True, help_text="Список тегов, связанных с рецептом."
    )
    ingredients = serializers.SerializerMethodField(
        help_text="Список ингредиентов с их количеством."
    )
    is_favorited = serializers.SerializerMethodField(
        help_text="Показывает, добавлен ли рецепт"
        "в избранное текущим пользователем."
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        help_text="Показывает, находится ли рецепт"
        "в корзине покупок текущего пользователя."
    )

    class Meta:
        """Метаданные сериализатора."""

        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        """Возвращает список ингредиентов рецепта с их количеством."""
        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipeingredient__amount')
        )

    def get_recipe(self, obj, model):
        """Связан ли рецепт с текущим пользователемчерез указанную модель."""
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return model.objects.filter(user=request.user, recipe=obj).exists()
        return False

    def filter_queryset_by_tags(self, queryset):
        """Фильтрует рецепты по тегам с использованием логики OR."""
        request = self.context.get('request')
        tag_slugs = request.query_params.getlist('tags')
        if tag_slugs:
            query = Q()
            for slug in tag_slugs:
                query |= Q(tags__slug=slug)
            return queryset.filter(query).distinct()
        return queryset

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное текущим пользователем."""
        return self.get_recipe(obj, FavoriteRecipe)

    def get_is_in_shopping_cart(self, obj):
        """Находится ли рецепт в корзине покупок текущего пользователя."""
        return self.get_recipe(obj, ShoppingCart)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления или изменения ингредиентов в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        help_text='Идентификатор существующего ингредиента.'
    )
    amount = serializers.IntegerField(
        write_only=True,
        min_value=MIN_INGREDIENTS,
        max_value=MAX_INGREDIENTS,
        help_text=f'Количество ингредиента.'
        f'Значение должно быть между {MIN_INGREDIENTS} и {MAX_INGREDIENTS}.'
    )

    class Meta:
        """Метаданные сериализатора."""

        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов через POST/PATCH."""

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
        allow_empty=False
    )
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=True, allow_null=False)
    name = serializers.CharField(required=True, max_length=256)
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME
    )

    class Meta:
        """Метаданные сериализатора."""

        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )

    def validate(self, data):
        """Проверка данных рецепта.

        1. Проверка наличия тегов в рецепте.
        2. Теги не должны повторяться.
        3. Проверка наличия ингредиентов в рецепте.
        4. Ингредиенты не должны повторяться.
        5. Проверка существования тегов и ингредиентов в базе данных.
        """
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Рецепт не может быть без тегов!'}
            )

        tags_list = [tag.id for tag in tags]
        if len(tags_list) != len(set(tags_list)):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны повторяться!'}
            )

        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Рецепт не может быть без ингредиентов!'}
            )

        ingredients_list = [item['id'].id for item in ingredients]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны повторяться!'}
            )

        get_list_or_404(Tag, id__in=tags_list)
        get_list_or_404(Ingredient, id__in=ingredients_list)

        return data

    def add_tags_ingredients(self, recipe, tags, ingredients):
        """Удаление старых тегов и ингредиентов, а затем добавление новых."""
        RecipeTag.objects.filter(recipe=recipe).delete()
        RecipeIngredient.objects.filter(recipe=recipe).delete()

        RecipeTag.objects.bulk_create([
            RecipeTag(recipe=recipe, tag=tag) for tag in tags
        ])

        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])

    def create(self, validated_data):
        """Создание нового рецепта с привязкой тегов и ингредиентов."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags_ingredients(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта с возможностью изменить теги и ингредиенты."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        self.add_tags_ingredients(instance, tags, ingredients)

        instance.save()
        return instance

    def to_representation(self, instance):
        """Преобразование данных рецепта в формат ответа."""
        return RecipeGetSerializer(instance).data


class RecipeListSerializer(serializers.ModelSerializer):
    """GET-сериализатор для отображения мини-рецептов."""

    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        """Метаданные сериализатора."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserRecepieSerializer(serializers.Serializer):
    """Сериализатор для обработки запросов с рецептами."""

    def validate(self, data):
        """Проверяет действия пользователя с рецептом.

        В зависимости от действия (add/del), сериализатор проверяет,
        существует ли рецепт и не пытается добавить или удалить рецепт,
        если это не разрешено.
        """
        user = self.context['request'].user
        recipe_id = self.context.get('recipe_pk')
        action = self.context.get('action')
        model = self.context.get('model')
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        if not recipe:
            raise serializers.ValidationError(
                'Данный рецепт не существует!'
            )

        userrecipe = model.objects.filter(user=user, recipe=recipe)
        if action == 'del':
            if not userrecipe:
                raise serializers.ValidationError(
                    'Данный рецепт не существует!'
                )

        if action == 'add':
            if userrecipe:
                raise serializers.ValidationError(
                    'Данный рецепт уже существует!'
                )

        return data

    def create(self, validated_data):
        """Создает запись о рецепте для пользователя.

        Добавляет рецепт в список пользователя.
        Если рецепт не существует, выбрасывает ошибку.
        """
        model = self.context.get('model')
        recipe = get_object_or_404(Recipe, pk=validated_data.get('pk'))
        model.objects.create(
            user=self.context['request'].user,
            recipe=recipe
        )
        return RecipeListSerializer(recipe)


class SubscriptionSerializer(serializers.Serializer):
    """Сериализатор для обработки POST-запросов на создание подписки."""

    def validate(self, data):
        """Проверка данных при оформлении подписки.

        Проверяет, что:
        - пользователь не может подписаться на самого себя;
        - подписка не может быть удалена, если её не существует;
        - подписка не может быть добавлена, если она уже существует.
        """
        user = self.context['request'].user
        subs_id = self.context.get('user_pk')
        action = self.context.get('action')

        subs = get_object_or_404(User, pk=subs_id)

        if user == subs:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )

        subscription = user.following.filter(author=subs).first()
        if action == 'delete_subs' and not subscription:
            raise serializers.ValidationError(
                'Данной подписки не существует!'
            )
        if action == 'create_subs' and subscription:
            raise serializers.ValidationError(
                'Данная подписка уже существует!'
            )
        return data

    def create(self, validated_data):
        """Создает новую подписку пользователя на другого пользователя."""
        request_user = self.context['request'].user
        limit_param = self.context.get('limit_param')
        author_id = self.context.get('user_pk')
        author = get_object_or_404(User, pk=author_id)

        subscription, created = Subscription.objects.get_or_create(
            user=request_user,
            author=author
        )

        if not created:
            raise serializers.ValidationError(
                'Данная подписка уже существует!'
            )

        return UserSubscriptionsSerializer(
            author,
            context={'limit_param': limit_param}
        ).data


class UserSubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для получения подписок пользователей."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        """Метаданные сериализатора."""

        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_recipes_count(self, obj):
        """Получение количества рецептов пользователя."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Получение списка рецептов пользователя."""
        recipes = obj.recipes.all()

        if limit_param := self.context.get('limit_param'):
            recipes = recipes[:int(limit_param)]

        serializer = RecipeListSerializer(recipes, many=True, read_only=True)
        return serializer.data
