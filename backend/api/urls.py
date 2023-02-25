from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import UserSubscribtionsViewSet, UsersViewSet, UserViewSet

router = DefaultRouter()

router.register(
    'users/subscriptions',
    UserSubscribtionsViewSet,
    basename='users_subscriptions'
)
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')
router.register('users', UsersViewSet, basename='users')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
