"""Модуль представлений API."""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

import short_url
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
)
from django_filters.rest_framework import DjangoFilterBackend

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import ApiPagination
from api.permissions import IsOwnerOrAdmin
from api.serializers import (
    IngredientSerializer, RecipeGetSerializer, RecipePostSerializer,
    SubscriptionSerializer, TagSerializer, UserGetSerializer,
    UserRecepieSerializer, UserSubscriptionsSerializer
)
from foodgram import settings
from recipes.models import (
    FavoriteRecipe, Ingredient, Recipe, RecipeIngredient, ShoppingCart,
    Subscription, Tag, User
)


def redirect_view(request, short_link):
    """Перенаправляет по короткому URL на страницу рецепта."""
    try:
        pk = short_url.decode_url(short_link)
        return redirect(f'/recipes/{pk}/')
    except Exception as error:
        return HttpResponse(
            f"Ошибка при декодировании ссылки: {error}",
            status=HTTP_400_BAD_REQUEST
        )


class UserViewSet(DjoserUserViewSet):
    """
    ViewSet для работы с пользователями и подписками.

    CRUD-операции для пользователей, профиля и подписок:
    - Просмотр всех пользователей
    - Просмотр отдельного пользователя
    - Просмотр и редактирование профиля текущего пользователя
    - Управление аватаром пользователя
    - Получение списка подписок
    - Операции подписки/отписки
    """

    queryset = User.objects.all()
    pagination_class = ApiPagination
    serializer_class = UserGetSerializer

    def get_serializer_class(self):
        """Выбор класса сериализатора в зависимости от действия."""
        if self.action in ['all_users', 'single_user', 'me']:
            return UserGetSerializer
        elif self.action == 'following':
            return UserSubscriptionsSerializer
        elif self.action == 'avatar':
            return UserGetSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        """Получение контекста сериализатора с добавлением запроса."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def all_users(self, request):
        """Возвращает список всех пользователей с пагинацией."""
        users = self.queryset
        paginated_queryset = self.paginate_queryset(users)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def single_user(self, request, pk=None):
        """Возвращает конкретного пользователя по ID."""
        user = get_object_or_404(User, pk=pk)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        """Показывает профиль текущего аутентифицированного пользователя."""
        serializer = UserGetSerializer(request.user)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(
        detail=False,
        url_path=r'me/avatar',
        permission_classes=(IsAuthenticated,)
    )
    def avatar(self, request):
        """Управление аватаром пользователя."""
        pass

    @avatar.mapping.put
    def set_avatar(self, request):
        """Добавление аватара пользователю."""
        user = get_object_or_404(User, pk=request.user.id)
        serializer = UserGetSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'avatar': serializer.data.get('avatar')},
            status=HTTP_200_OK
        )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара у текущего пользователя."""
        User.objects.filter(pk=request.user.id).update(avatar=None)
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Возвращение списка подписок текущего пользователя."""
        users = User.objects.filter(followers__user=request.user)
        limit_param = request.query_params.get('recipes_limit')
        paginated_queryset = self.paginate_queryset(users)
        serializer = UserSubscriptionsSerializer(
            paginated_queryset,
            context={'limit_param': limit_param},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """Операции подписки и отписки от пользователя."""
        pass

    @subscribe.mapping.post
    def create_subs(self, request, id):
        """Операция подписки на пользователя."""
        limit_param = request.query_params.get('recipes_limit')
        serializer = SubscriptionSerializer(
            data=request.data,
            context={
                'request': request,
                'user_pk': id,
                'limit_param': limit_param,
                'action': 'create_subs'
            }
        )
        serializer.is_valid(raise_exception=True)
        subs = serializer.save(pk=id)
        return Response(subs, status=HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subs(self, request, id):
        """Операция отписки от пользователя."""
        serializer = SubscriptionSerializer(
            data=request.data,
            context={
                'request': request,
                'user_pk': id,
                'action': 'delete_subs'
            }
        )
        serializer.is_valid(raise_exception=True)
        get_object_or_404(
            Subscription,
            user=self.request.user,
            author=get_object_or_404(User, pk=id)
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ['name']


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD-операции для рецептов."""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = ApiPagination

    def get_permissions(self):
        """Устанавливает разрешения для действий."""
        if self.action in ('list', 'retrieve', 'get_short_link'):
            return (AllowAny(),)
        return (IsAuthenticated(), IsOwnerOrAdmin())

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """Добавление/удаление рецепта из избранного."""
        pass

    @favorite.mapping.post
    def add_into_favorite(self, request, pk):
        """Добавляет рецепт в избранное пользователя."""
        serializer = UserRecepieSerializer(
            data=request.data,
            context={
                'request': request,
                'recipe_pk': pk,
                'action': 'add',
                'model': FavoriteRecipe
            }
        )
        serializer.is_valid(raise_exception=True)
        short_recipe = serializer.save(pk=pk)
        return Response(short_recipe.data, status=HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk):
        """Удаляет рецепт из избранного пользователя."""
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite_recipe = FavoriteRecipe.objects.filter(
            user=self.request.user,
            recipe=recipe
        )
        if not favorite_recipe.exists():
            return Response(
                {"detail": "Рецепт не был найден в избранном."},
                status=HTTP_400_BAD_REQUEST
            )
        deleted_count, _ = favorite_recipe.delete()
        if deleted_count:
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Не удалось удалить рецепт из избранного."},
            status=HTTP_400_BAD_REQUEST
        )

    @action(detail=True, permission_classes=(AllowAny,), url_path='get-link')
    def get_short_link(self, request, pk):
        """Генерирует короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)

        short_link = short_url.encode_url(recipe.id)
        recipe.short_url = short_link
        recipe.save()

        url = f'{"https" if request.is_secure() else "http"}://{request.get_host()}/s/{short_link}/'

        return Response({'short-link': url}, status=HTTP_200_OK)

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Операции со списком покупок (добавление/удаление)."""
        pass

    @shopping_cart.mapping.post
    def add_into_shopping_cart(self, request, pk):
        """Добавляет рецепт в список покупок пользователя."""
        serializer = UserRecepieSerializer(
            data=request.data,
            context={
                'request': request,
                'recipe_pk': pk,
                'action': 'add',
                'model': ShoppingCart
            }
        )
        serializer.is_valid(raise_exception=True)
        short_recipe = serializer.save(pk=pk)
        return Response(short_recipe.data, status=HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk):
        """Удаляет рецепт из списка покупок пользователя."""
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_cart_recipe = ShoppingCart.objects.filter(
            user=self.request.user,
            recipe=recipe
        )
        deleted_count, _ = shopping_cart_recipe.delete()
        if deleted_count:
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Рецепт не найден в списке покупок."},
            status=HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Скачивает список покупок пользователя в txt-файл."""
        shopping_cart = ShoppingCart.objects.filter(user=request.user)

        if not shopping_cart.exists():
            return Response({'detail': 'Список покупок пуст'}, status=404)

        ingredients = {}

        for item in shopping_cart:
            recipe = item.recipe
            for recipe_ingredient in RecipeIngredient.objects.filter(
                recipe=recipe
            ):
                ingredient = recipe_ingredient.ingredient
                name = ingredient.name
                unit = ingredient.measurement_unit
                amount = recipe_ingredient.amount
                if name in ingredients:
                    ingredients[name]['amount'] += amount
                else:
                    ingredients[name] = {'amount': amount, 'unit': unit}

        content = 'Список покупок:\n'
        for name, data in ingredients.items():
            content += f"{name} — {data['amount']} {data['unit']}\n"

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response
