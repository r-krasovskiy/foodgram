"""Зона администратра проекта."""

from django.contrib import admin

from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Recipe, ShoppingList, Subscription, Tag
)



class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',)
    list_filter = ('name',)
    search_fields = ('name',)

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name',)
    list_filter = ('tags', 'picture',)
    search_fields = ('author', 'name')

class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measure',)
    list_filter = ('measure',)
    search_fields = ('name',)

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe',)
    search_fields = ('author',)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = ('author',)

class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe',)
    search_fields = ('author',)


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    list_filter = ('recipe', 'ingredient',)
    search_fields = ('name',)


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(Tag, TagAdmin)