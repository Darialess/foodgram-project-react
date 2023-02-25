from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Recipe
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from django.contrib.auth.hashers import make_password
from .models import Subscribe, User



class UserSerializer(serializers.ModelSerializer):
    """ Сериализаторор для модели User."""

    is_subscribed = serializers.SerializerMethodField()
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    def get_is_subscribed(self, obj):
        if not self.context.get('request') or (
                self.context.get('request') is None):
            return False
        request = self.context.get('request')
        user = request.user
        subcribe = user.follower.filter(author=obj)
        return subcribe.exists()

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
            'is_subscribed'
        ]


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


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeListSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes_author.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if not recipes_limit:
            return ShortRecipeSerializer(
                Recipe.objects.filter(author=obj),
                many=True,
                context={'request': request}
            ).data
        return ShortRecipeSerializer(
            Recipe.objects.filter(author=obj)[:int(recipes_limit)],
            many=True,
            context={'request': request}
        ).data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user
        if not request or user.is_anonymous:
            return False
        subcribe = user.follower.filter(author=obj)
        return subcribe.exists()


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('author', 'user')

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeListSerializer(
            instance.author,
            context={'request': request}
        ).data

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        author = data.get('author')
        if Subscribe.objects.filter(user=user, author=author):
            raise serializers.ValidationError('Вы уже подписаны')
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя'
            )
        return data


class SetPasswordSerializer(serializers.ModelSerializer):
    """ Сериализатор эндпойнта SetPassword. """
    new_password = serializers.CharField(
        required=True,
        max_length=50,
        min_length=8,
        write_only=True
    )
    current_password = serializers.CharField(
        required=True,
        max_length=50,
        min_length=4,
        write_only=True
    )

    class Meta:
        model = User
        fields = ['new_password', 'current_password']

    def validate(self, attrs):
        if attrs['new_password'] == attrs['current_password']:
            raise serializers.ValidationError(
                'новый и старый пароли совпадают'
            )
        return super().validate(attrs)


class UserSubscribtionsSerializer(serializers.ModelSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
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
            'recipes',
            'recipes_count',
        ]

    def get_recipes(self, obj):
        recipes_limit = self.context['recipes_limit']
        recipes = Recipe.objects.filter(author_id=obj.id)[:recipes_limit]
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author_id=obj.id)
        return recipes.count()

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=self.context.get('user'),
            author=obj
        ).exists()

    def update(self, instance, validated_data):
        author = User.objects.get(username=self.context.get('author'))
        instance.email = author.email
        return instance


class FollowSerializer(serializers.ModelSerializer):
    """ Сериализатор модели Follow. """

    result = UserSubscribtionsSerializer()

    class Meta:
        model = Subscribe
        fields = '__all__'
