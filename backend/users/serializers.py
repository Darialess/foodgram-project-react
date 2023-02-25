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
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

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
    """ Сериализатор эндпойнта UserSubscribtions. """

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
        return Subscribe.objects.filter(
            user=self.context.get('user'),
            author=obj
        ).exists()

    def update(self, instance, validated_data):
        author = User.objects.get(username=self.context.get('author'))
        instance.email = author.email
        return instance


class SubscribeSerializer(serializers.ModelSerializer):
    result = UserSubscribtionsSerializer()

    class Meta:
        model = Subscribe
        fields = '__all__'
