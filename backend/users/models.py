from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models



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
    is_subscribed = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Автор рецепта",
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