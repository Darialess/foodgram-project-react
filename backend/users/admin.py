from django.contrib import admin
from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = [
        'pk',
        'username',
        'email',
        'first_name',
        'is_active',
        'last_name',
        'is_subscribed',
    ]
    search_fields = ['email']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['user', 'author']