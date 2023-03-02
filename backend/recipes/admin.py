from django.contrib import admin
from django.contrib.admin import display

from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag)


class IngredientInline(admin.TabularInline):
    model = IngredientAmount


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'added_in_favorites')
    readonly_fields = ('added_in_favorites',)
    search_fields = ('name', 'author', 'tags')
    list_filter = ('author', 'name', 'tags',)
    inlines = [
        IngredientInline,
    ]

    @display(description='Количество в избранных')
    def added_in_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    empty_value_display = '-пусто-'
