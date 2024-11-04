"""Модуль представлений проекта."""

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_403_FORBIDDEN,
    HTTP_405_METHOD_NOT_ALLOWED
)

from djoser.views import UserViewSet as UVS
from api.serializers import (
    UserGetSerializer,
    UserPostSerializer,
    FollowSerializer,
    UserFollowSerializer,
    IngredientSerializer,
    ShoppingListSerializer,
    TagSerializer,
    RecipeReadSerializer,
    RecipeSerializer,
    RecipeWriteSerializer
)

from recipes.models import (Recipe, User, Follow, Tag, Ingredient)
from rest_framework.permissions import (AllowAny, IsAuthenticated,)
from api.permissions import IsOwnerOrAdmin
from api.filters import RecipeFilter
from api.pagination import ApiPagination

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = ApiPagination
    serializer_class = UserGetSerializer

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от выполняемого действия."""
        if self.action in ['list', 'all_users', 'one_user', 'current_user']:
            return UserGetSerializer
        elif self.action == 'following':
            return UserFollowSerializer
        elif self.action == 'avatar':
            return UserGetSerializer
        return super().get_serializer_class()

    def all_users(self, request):
        """Возвращает список всех пользователей."""
        users = self.queryset
        paginated_queryset = self.paginate_queryset(users)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)
    
    def one_user(self, request, pk=None):
        """Возвращает данные конкретного пользователя по его ID."""
        user = get_object_or_404(User, pk=pk)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=HTTP_200_OK)

    def current_user(self, request):
        """Возвращает профиль текущего пользователя."""
        if not request.user.is_authenticated:
            return Response(status=HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=HTTP_200_OK)
    
    def avatar(self, request):
        """Методы работы с аватаром."""
        if not request.user.is_authenticated:
            return Response(status=HTTP_403_FORBIDDEN)
        
        if request.method == 'PUT':
            user = get_object_or_404(User, pk=request.user.id)
            serializer = self.get_serializer(user, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'avatar': serializer.data.get('avatar')})
        
        elif request.method == 'DELETE':
            User.objects.filter(pk=request.user.id).update(avatar=None)
            return Response(status=HTTP_204_NO_CONTENT)
        
        return Response(status=HTTP_405_METHOD_NOT_ALLOWED)

    def following(self, request, id=None):
        """Методы работы с подписками."""
        if not request.user.is_authenticated:
            return Response(status=HTTP_403_FORBIDDEN)
        
        if request.method == 'GET':
            users = User.objects.filter(followers__user=request.user)
            limit_param = request.query_params.get('recipes_limit')
            paginated_queryset = self.paginate_queryset(users)
            serializer = self.get_serializer(paginated_queryset, context={'limit_param': limit_param}, many=True)
            return self.get_paginated_response(serializer.data)
        
        elif request.method == 'POST' and id is not None:
            limit_param = request.query_params.get('recipes_limit')
            serializer = FollowSerializer(
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
            return Response(subs.data, status=HTTP_201_CREATED)

        elif request.method == 'DELETE' and id is not None:
            serializer = FollowSerializer(
                data=request.data,
                context={
                    'request': request,
                    'user_pk': id,
                    'action': 'delete_subs'
                }
            )
            serializer.is_valid(raise_exception=True)
            get_object_or_404(Follow, user=request.user, cooker=get_object_or_404(User, pk=id)).delete()
            return Response(status=HTTP_204_NO_CONTENT)
    
        return Response(status=HTTP_405_METHOD_NOT_ALLOWED)



class TagViewSet(viewsets.ModelViewSet):
    """Представление модели тегов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = (AllowAny,)
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление модели рецептов."""

    queryset = Recipe.objects.all()
    pagination_class = ApiPagination

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'get_link'):
            return (AllowAny(),)
        return (IsAuthenticated(), IsOwnerOrAdmin())

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer


class ShoppingListViewSet(viewsets.ModelViewSet):
    """Представление модели списков покупок."""

    serializer_class = ShoppingListSerializer
    pass


class IngredientViewSet(viewsets.ModelViewSet):
    """Представление модели ингридиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeReadViewSet(viewsets.ModelViewSet):
    """Представление модели чтения рецептов."""

    serializer_class = RecipeReadSerializer
    pass


class RecipeWriteViewSet(viewsets.ModelViewSet):
    """Представление модели записи рецептов."""

    serializer_class = RecipeWriteSerializer
    pass
