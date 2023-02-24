from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action, api_view
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly, SAFE_METHODS
)
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from users.permissions import AdminOrAuthorOrReadOnly

from .pagination import LimitPageNumberPagination
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, TagSerializer, 
                          FavoriteSerializer, ShoppingCartSerializer)
from users.serializers import ShortRecipeSerializer
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST
)
from rest_framework.views import APIView
from rest_framework.exceptions import MethodNotAllowed


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitPageNumberPagination
    serializer_class = RecipeReadSerializer
    permission_classes = (AdminOrAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(user=request.user,
                                       recipe=recipe).exists():
                return Response({'detail': 'Рецепт уже добавлен в избранное.'},
                                status=status.HTTP_400_BAD_REQUEST)
            new_fav = Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = FavoriteSerializer(new_fav,
                                            context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            old_fav = get_object_or_404(Favorite,
                                        user=request.user,
                                        recipe=recipe)
            self.perform_destroy(old_fav)
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise MethodNotAllowed(request.method)


    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk)
        else:
            return self.delete_from(ShoppingCart, request.user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))
        shopping_list = ['{} ({}) - {}\n'.format(
            ingredient['ingredient__name'],
            ingredient['ingredient__measurement_unit'],
            ingredient['total_amount']
        ) for ingredient in ingredients]
        response = HttpResponse(shopping_list, content_type='text/plain')
        attachment = 'attachment; filename="shopping_list.txt"'
        response['Content-Disposition'] = attachment
        return response



class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
