from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet

from .views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import UserVievSet

router = DefaultRouter()

router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:id>/subscribe/', FollowApiView.as_view(),
         name='subscribe'),
    path('users/subscriptions/', FollowListAPIView.as_view(),
         name='subscription'),
]
