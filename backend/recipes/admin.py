from django.contrib import admin

from .models import Ingredient, IngredientRecipe, Recipe, ShoppingCart, Tag, Favorite


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    list_filter = ('name', 'author', 'tag',)
    inlines = [
        IngredientInline,
    ]


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
