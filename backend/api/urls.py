from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UserSubscribtionsViewSet, UsersVievSet, UserVievSet

from .views import IngredientVievSet, RecipeVievSet, TagsViewSet

router = DefaultRouter()

router.register(
    'users/subscriptions',
    UserSubscribtionsViewSet,
    basename='users_subscriptions'
)
router.register('ingredients', IngredientVievSet, basename='ingredients')
router.register('users', UserVievSet, basename='users')
router.register('users', UsersVievSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipeVievSet, basename='recipes')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]