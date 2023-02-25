from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models


class UserManager(BaseUserManager):
    """ Manager для создания User. """

    def create_user(self, username, email, password=None, **extra_fields):
        """ Создает и возвращает пользователя с имэйлом, паролем и именем. """
        if username is None:
            raise TypeError('Пользователи должны иметь имя пользователя.')

        if email is None:
            raise TypeError('пользователи должны иметь email.')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """ Создаёт суперпользователя. """
        if password is None:
            raise TypeError('У Суперпользователя должен быть пароль.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """ Модель пользователя"""

    username = models.CharField(
        db_index=True,
        max_length=150,
        unique=True,
        verbose_name='Има пользователя ',
        help_text='Логин пользователя'
    )
    email = models.EmailField(
        db_index=True,
        max_length=254,
        unique=True,
        verbose_name='Email',
        help_text='email пользователя'
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        default=' ',
        verbose_name='Имя',
        help_text='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        default=' ',
        verbose_name='Фамилия',
        help_text='Фамилия пользователя'
    )
    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    is_subscribed = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            )
        ]

    def __str__(self):
        return self.username


class Follow(models.Model):
    """ Модель подписки на авторов"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name="Подписчик",
        help_text='тот кто подписывается ',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Автор рецепта",
        help_text='тот на кого подписываются',
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_author_user'
            )
        ]

    def __str__(self):
        return "Подписка на автора"