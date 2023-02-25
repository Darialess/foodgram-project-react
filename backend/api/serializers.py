from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag, TagsRecipe)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.serializers import CustomUserSerializer, ShortRecipeSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsEditSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка ингредиентов в рецепте с указанием
    количества."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта."""
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(
        max_length=None,
        use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    ingredients = IngredientsEditSerializer(
        many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        ingredients = data['ingredients']
        ingredient_list = []

        for ingredient in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиент не может повторятся')
            ingredient_list.append(ingredient)

        for ingredient in ingredients:
            amount = ingredient['amount']
            if int(amount) < 1:
                raise serializers.ValidationError(
                    {'amount': 'Количество ингредиента не может быть равным 0'}
                )
        data['ingredients'] = ingredients
        return data

    def create_ingredients(self, ingredients, recipe):
        bulk_ingredient_list = [
            IngredientRecipe(
                recipe=recipe,
                ingredient=get_object_or_404(
                    Ingredient, pk=ingredient_data['id']),
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients
        ]
        IngredientRecipe.objects.bulk_create(bulk_ingredient_list)

    def create_tags(self, tags, recipe):
        bulk_tags_list = [
            TagsRecipe(recipe=recipe,
                       tags=get_object_or_404(Tag, name=tag_data)
                       )
            for tag_data in tags
        ]
        TagsRecipe.objects.bulk_create(bulk_tags_list)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context.get('request').user
        recipe = super().create(validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        IngredientRecipe.objects.filter(recipe=instance).all().delete()
        self.create_ingredients(validated_data.get('ingredients'), instance)
        instance.save()
        return instance

    def validate_ingredients(self, value):
        list = []
        for ing in value:
            ing_id = dict(ing).get('id')
            if ing_id in list:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться!'
                )
            list.append(ing_id)
        if not list:
            raise serializers.ValidationError(
                'В рецепте должны быть ингредиенты'
            )
        return value

    def validate_cooking_time(self, value):
        if value == 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше нуля.'
            )
        return value

    def validate_tags(self, value):
        list = []
        for tag in value:
            if tag in list:
                raise serializers.ValidationError(
                    'Теги не должны повторяться!'
                )
            list.append(tag)
        return value

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода рецепта."""
    image = Base64ImageField()
    tags = TagSerializer(
        many=True,
        read_only=True)
    author =  CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe_id=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe_id=obj
        ).exists()


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины покупок."""
   
    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]
