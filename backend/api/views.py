"""Модуль представлений API."""
import short_url
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404, redirect
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
)
from djoser.views import UserViewSet as DjoserUserViewSet
from api.serializers import (UserGetSerializer, UserPostSerializer,
                             SubscriptionSerializer, 
                             UserSubscriptionsSerializer, IngredientSerializer, 
                             TagSerializer, RecipeGetSerializer,
                             RecipePostSerializer, UserRecepieSerializer
)
from recipes.models import (Recipe, User, Subscription, Tag, Ingredient, 
                            ShoppingCart, FavoriteRecipe)
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.permissions import IsOwnerOrAdmin
from api.filters import IngredientFilter, RecipeFilter
from api.pagination import ApiPagination
from rest_framework.decorators import action
from foodgram import settings


def redirect_view(request, s):
    """Перенаправление по короткому URL."""
    pk = short_url.decode_url(s)
    return redirect(f'/recipes/{pk}/')


class UserViewSet(DjoserUserViewSet):
    """
    ViewSet для работы с пользователями и подписками.

    Реализует CRUD операции для пользователей, профиля и подписок.
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

    @action(detail=False, methods=('get',), permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Показывает профиль текущего аутентифицированного пользователя."""
        serializer = UserGetSerializer(request.user)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(detail=False, url_path=r'me/avatar', permission_classes=(IsAuthenticated,))
    def avatar(self, request):
        """Управление аватаром пользователя."""
        pass

    @avatar.mapping.put
    def set_avatar(self, request):
        """Добавление аватара пользователю."""
        user = get_object_or_404(User, pk=request.user.id)
        serializer = UserGetSerializer(
            user, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'avatar': serializer.data.get('avatar')}, status=HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаляет аватар текущего пользователя."""
        User.objects.filter(pk=request.user.id).update(avatar=None)
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Возвращает список подписок текущего пользователя."""
        users = User.objects.filter(followers__user=request.user)
        limit_param = request.query_params.get('recipes_limit')
        paginated_queryset = self.paginate_queryset(users)
        serializer = SubscriptionSerializer(paginated_queryset, context={'limit_param': limit_param}, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """Операции подписки или отмены подписки на пользователя."""
        pass

    @subscribe.mapping.post
    def create_subs(self, request, id):
        """Подписывается на пользователя."""
        limit_param = request.query_params.get('recipes_limit')
        serializer = SubscriptionSerializer(data=request.data, context={'request': request, 'user_pk': id, 'limit_param': limit_param, 'action': 'create_subs'})
        serializer.is_valid(raise_exception=True)
        subs = serializer.save(pk=id)
        return Response(subs.data, status=HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subs(self, request, id):
        """Отменяет подписку на пользователя."""
        serializer = SubscriptionSerializer(data=request.data, context={'request': request, 'user_pk': id, 'action': 'delete_subs'})
        serializer.is_valid(raise_exception=True)
        get_object_or_404(Subscription, user=self.request.user, cooker=get_object_or_404(User, pk=id)).delete()
        return Response(status=HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet для работы с тегами.

    Позволяет получать информацию о тегах.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet для работы с ингредиентами.

    Позволяет получать ингредиенты и фильтровать их по имени.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ['name']


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для рецептов.

    Поддерживает CRUD операции, добавление/удаление из избранного,
    операции со списком покупок и создание коротких ссылок.
    """

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = ApiPagination

    def get_permissions(self):
        """Устанавливает разрешения в зависимости от действия."""
        if self.action in ('list', 'retrieve', 'get_link'):
            return (AllowAny(),)
        return (IsAuthenticated(), IsOwnerOrAdmin())

    def get_serializer_class(self):
        """Выбор класса сериализатора в зависимости от действия."""
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """Добавление/удаление рецепта из избранного."""
        pass

    @favorite.mapping.post
    def add_into_fav(self, request, pk):
        """Добавляет рецепт в избранное пользователя."""
        serializer = UserRecepieSerializer(data=request.data, context={'request': request, 'recipe_pk': pk, 'action': 'add', 'model': FavoriteRecipe})
        serializer.is_valid(raise_exception=True)
        short_recipe = serializer.save(pk=pk)
        return Response(short_recipe.data, status=HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk):
        """Удаляет рецепт из избранного пользователя."""
        serializer = UserRecepieSerializer(data=request.data, context={'request': request, 'recipe_pk': pk, 'action': 'del', 'model': FavoriteRecipe})
        serializer.is_valid(raise_exception=True)
        get_object_or_404(FavoriteRecipe, user=self.request.user, recipe=get_object_or_404(Recipe, pk=pk)).delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=True, permission_classes=(AllowAny,), url_path='get-link')
    def get_short_link(self, request, pk):
        """Генерирует короткую ссылку на рецепт."""
        url = f'http://{settings.ALLOWED_HOSTS[0]}/s/{short_url.encode_url(int(pk))}/'
        return Response({'short-link': url}, status=HTTP_200_OK)

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Операции со списком покупок (добавление/удаление)."""
        pass

    @shopping_cart.mapping.post
    def add_into_shopping_cart(self, request, pk):
        """Добавляет рецепт в список покупок пользователя."""
        serializer = UserRecepieSerializer(data=request.data, context={'request': request, 'recipe_pk': pk, 'action': 'add', 'model': ShoppingCart})
        serializer.is_valid(raise_exception=True)
        short_recipe = serializer.save(pk=pk)
        return Response(short_recipe.data, status=HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk):
        """Удаляет рецепт из списка покупок пользователя."""
        serializer = UserRecepieSerializer(data=request.data, context={'request': request, 'recipe_pk': pk, 'action': 'del', 'model': ShoppingCart})
        serializer.is_valid(raise_exception=True)
        get_object_or_404(ShoppingCart, user=self.request.user, recipe=get_object_or_404(Recipe, pk=pk)).delete()
        return Response(status=HTTP_204_NO_CONTENT)
