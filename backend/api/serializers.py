from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag, TagsRecipe)
from users.serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError 


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientAmountSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода количества ингредиентов
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения рецептов
    """
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        queryset = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()


class AddIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления Ингредиентов
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания нового рецепта
    """
    image = Base64ImageField( 
        max_length=None, 
        use_url=True) 
    tags = serializers.PrimaryKeyRelatedField( 
        many=True, 
        queryset=Tag.objects.all()) 
    ingredients = AddIngredientSerializer( 
        many=True) 

    class Meta: 
        model = Recipe 
        fields = '__all__' 
        read_only_fields = ('author',) 

    def validate_ingredients(self, value): 
        ingredients = value 
        if not ingredients: 
            raise ValidationError({ 
                'ingredients': 'Нужен хотя бы один ингредиент!' 
            }) 
        ingredients_list = [] 
        for item in ingredients: 
            ingredient = get_object_or_404(Ingredient, id=item['id']) 
            if ingredient in ingredients_list: 
                raise ValidationError({ 
                    'ingredients': 'Ингридиенты не могут повторяться!' 
                }) 
            ingredients_list.append(ingredient) 
        return value 

    def validate_tags(self, value): 
        tags = value 
        if not tags: 
            raise ValidationError({ 
                'tags': 'Нужно выбрать хотя бы один тег!' 
            }) 
        tags_list = [] 
        for tag in tags: 
            if tag in tags_list: 
                raise ValidationError({ 
                    'tags': 'Теги должны быть уникальными!' 
                }) 
            tags_list.append(tag) 
        return value 

    def create_ingredients(self, ingredients, recipe): 
        for ingredient in ingredients: 
            Ingredient.objects.create( 
                recipe=recipe, 
                ingredient_id=ingredient.get('id'), 
                amount=ingredient.get('amount'), ) 

    def create(self, validated_data): 
        ingredients = validated_data.pop('ingredients') 
        tags = validated_data.pop('tags') 
        recipe = Recipe.objects.create(**validated_data) 
        recipe.tags.set(tags) 
        self.create_ingredients(ingredients, recipe) 
        return recipe 

    def to_representation(self, instance): 
        return RecipeListSerializer( 
            instance, 
            context={ 
                'request': self.context.get('request') 
            }).data 

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
        IngredientAmount.objects.filter(recipe=instance).all().delete()
        self.create_ingredients(validated_data.get('ingredients'), instance)
        instance.save()
        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткого отображения сведений о рецепте
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка избранного
    """
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError({
                'status': 'Рецепт уже есть в избранном!'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(
            instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка покупок
    """
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(
            instance.recipe, context=context).data