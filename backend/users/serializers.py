from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.serializers import ShopingCardSerializer
from recipes.models import Recipe
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):

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


class RegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'token',
            'is_subscribed'
        ]

    def validate(self, data):
        if data['username'].lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть me'
            )
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                'email не соответствует User'
            )
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class SetPasswordSerializer(serializers.ModelSerializer):
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
        serializer = ShopingCardSerializer(recipes, many=True)
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

    result = UserSubscribtionsSerializer()

    class Meta:
        model = Follow
        fields = '__all__'


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