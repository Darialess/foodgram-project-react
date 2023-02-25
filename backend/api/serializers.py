from django.contrib.auth.hashers import make_password
from django.core.validators import MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from recipes.models import (Favorite, IngredientAmount, Ingredients, Recipe,
                            Tags, TagsRecipe)
from users.models import User


class UsersSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        ]

    def get_is_subscribed(self, obj):

        if not self.context.get('request') or (
                self.context.get('request') is None):
            return False
        request = self.context.get('request')
        user = request.user
        subcribe = user.follower.filter(author=obj)
        return subcribe.exists()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    def create(self, validated_data):
        password = validated_data['password']
        validated_data['password'] = make_password(password)
        return super().create(validated_data)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        ]


class IngredientsSerializer(serializers.ModelSerializer):
    """ Сериализаторор для модели Ingredient."""

    class Meta:
        model = Ingredients
        fields = [
            'id',
            'name',
            'measurement_unit'
        ]


class IngredientAmountSerializer(serializers.ModelSerializer):
    """ Сериализаторор для модели IngredientAmount."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientAmount
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount',
        ]


class TagsSerializer(serializers.ModelSerializer):
    """ Сериализаторор для модели Tags."""
    name = serializers.SerializerMethodField()

    class Meta:
        model = Tags
        fields = [
            'id',
            'name',
            'color',
            'slug'
        ]


class AmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount',)


class RecipeSerialzer(serializers.ModelSerializer):

    tags = TagsSerializer(many=True)
    author = UsersSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        ]

    def get_ingredients(self, obj):
        ingredients = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return UserShopCart.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()


class CreateRecipeSerialzer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = AmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(), many=True,
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(
            limit_value=1,
            message='Время приготовления не может занимать меньше минуты'
        ),)
    )

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        ]

    def validate(self, data):
        ingredients = data['ingredients']
        ingredient_list = []

        for ingredient in ingredients:
            ingredient = get_object_or_404(
                Ingredients, id=ingredient['id'])
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
            IngredientAmount(
                recipe=recipe,
                ingredient=get_object_or_404(
                    Ingredients, pk=ingredient_data['id']),
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients
        ]
        IngredientAmount.objects.bulk_create(bulk_ingredient_list)

    def create_tags(self, tags, recipe):
        bulk_tags_list = [
            TagsRecipe(recipe=recipe,
                       tags=get_object_or_404(Tags, name=tag_data)
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

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        instance = super().update(instance, validated_data)
        if tags:
            instance.tags.clear()
            instance.tags.set(tags)
        if ingredients:
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        return instance

    def to_representation(self, instance):
        return RecipeSerialzer(instance, context={
            'request': self.context.get('request')
        }).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]

