from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import mixins

from api.filters import Filter, NameSearchFilter
from users.permissions import IsAuthorOrReadOnly
from api.serializers import (CreateRecipeSerialzer, IngredientsSerializer,
                             RecipeSerialzer, ShoppingCartSerializer,
                             TagsSerializer)
from recipes.models import (Favorite, IngredientAmount, Ingredients, Recipe,
                            Tags, ShoppingCart)
from recipes.utilits import make_send_file


class TagsViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """ Представление модели Tags """
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientVievSet(viewsets.ReadOnlyModelViewSet):
    """ Представление модели Ingredient """
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (NameSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipesLimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class RecipeVievSet(viewsets.ModelViewSet):
    """ Представление модели Recipe """
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = Filter
    pagination_class = RecipesLimitPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerialzer
        return CreateRecipeSerialzer

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        name='download_shopping_cart')
    def download_shopping_cart(self, request):
        """ Скачать файл со списком ингредиентов """

        ingredient = IngredientAmount.objects.filter(
            recipe__usershopcart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount_sum=Sum('amount'))

        response = HttpResponse(make_send_file(ingredient).getvalue(),
                                content_type='text/plain')
        response['Content-Disposition'] = ('attachment;'
                                           'filename=shop_list_file')

        return response

    def add_recipe_to_fav_or_shopcart(self, request, pk, model):
        """Вспомогательная функция для добавления рецепта в
        shopping_cart или favorite."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = model.objects.filter(
            user=user,
            recipe=recipe
        )
        if request.method == 'POST':
            model.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            serializer = ShopingCardSerializer(recipe)
            serializer.validate(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        name='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        return self.add_recipe_to_fav_or_shopcart(request, pk, UserShopCart)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        name='favorite'
    )
    def favorite(self, request, pk=None):

        return self.add_recipe_to_fav_or_shopcart(request, pk, Favorite)