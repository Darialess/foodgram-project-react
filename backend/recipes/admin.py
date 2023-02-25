from django.contrib import admin

from .models import (Favorite, IngredientAmount, Ingredients, Recipe, Tags,
                     ShoppingCart)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'favorites'
    ]
    search_fields = ['text']

    def favorites(self, obj):

        return Favorite.objects.filter(recipe=obj).count()

    favorites.short_description = "Количество добавлений в избранное"


@admin.register(Ingredients)
class IngredientAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'name',
    ]
    search_fields = ['name']


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = [
        'recipe',
        'ingredient',
        'amount'
    ]


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'name',
        'color',
        'slug'
    ]


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'recipe'
    ]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'recipe'
    ]