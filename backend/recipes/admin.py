"""Зона администратра проекта."""

from django.contrib import admin

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Subscription, Tag)

from users.models import User


class TagAdmin(admin.ModelAdmin):
    """Отображение в админке тегов."""

    list_display = ('id', 'name', 'slug',)
    list_filter = ('name',)
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    """Отображение в админке рецептов."""

    list_display = ('id', 'author', 'name',)
    list_filter = ('tags', 'image',)
    search_fields = ('author', 'name')


class IngredientAdmin(admin.ModelAdmin):
    """Отображение в админке ингридиентов."""

    list_display = ('name', 'measurement_unit',)
    list_filter = ('measurement_unit',)
    search_fields = ('name',)


class FavoriteRecipeAdmin(admin.ModelAdmin):
    """Отображение в админке избранных рецептов."""

    list_display = ('user', 'recipe',)
    search_fields = ('user',)


class SubscriptionAdmin(admin.ModelAdmin):
    """Отображение в админке подписок пользователей."""

    list_display = ('user', 'author',)
    search_fields = ('author',)


class ShoppingCartAdmin(admin.ModelAdmin):
    """Отображение в админке списков покупок."""

    list_display = ('user', 'recipe',)
    search_fields = ('user',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    """Отображение в админке ингридиентов рецептов."""

    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    list_filter = ('recipe', 'ingredient',)
    search_fields = ('name',)


class UserAdmin(admin.ModelAdmin):
    """Отображение в админке информации о пользователях."""

    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
        'avatar', 'recipe_count', 'follower_count'
    )
    list_filter = ('is_superuser',)
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def recipe_count(self, obj):
        """Количество рецептов пользователя."""
        return obj.recipes.count()
    recipe_count.short_description = 'Количество рецептов'

    def follower_count(self, obj):
        """Количество подписчиков пользователя."""
        return Subscription.objects.filter(author=obj).count()


admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(User, UserAdmin)
