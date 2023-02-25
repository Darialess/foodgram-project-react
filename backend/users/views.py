from api.pagination import LimitPageNumberPagination
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from .models import Subscribe, User
from .serializers import UsersSerializer, UserSerializer, UserSubscribtionsSerializer, SetPasswordSerializer
from foodgram.settings import DEFAULT_RECIPE_LIMIT
from .permissions import IsOwnerOnly
from django.contrib.auth.hashers import make_password


class UsersVievSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UsersSerializer
        return UserSerializer


class UserVievSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsOwnerOnly],
        name='me'
    )
    def me(self, request, pk=None):
        data = UserSerializer(request.user, many=False).data
        return Response(data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        name='set_password'
    )
    def set_password(self, request):
        new_password = request.data.get('new_password')
        current_password = request.data.get('current_password')
        user = User.objects.get(username=request.user)
        serializer = SetPasswordSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        if user.check_password(current_password):
            serializer.save(password=make_password(new_password))
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Неверно введен текущий пароль'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        name='subscribe'
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST' and user != author:
            recipes_limit = int(request.POST.get(
                'recipes_limit', DEFAULT_RECIPE_LIMIT
            ))

            Subscribe.objects.get_or_create(user=user, author=author)
            serializer = UserSubscribtionsSerializer(
                author,
                data=request.data,
                partial=True,
                context={
                    'author': author,
                    'user': user,
                    'recipes_limit': recipes_limit

                }
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE' and Subscribe.objects.filter(
            user=user,
            author=author
        ).exists():
            Subscribe.objects.get(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            'User + Author ошибка модели Follow',
            status=status.HTTP_400_BAD_REQUEST
        )


class UserSubscribtionsViewSet(viewsets.ModelViewSet):
    """ Список авторов на которых подписан пользователь """
    permission_classes = [IsOwnerOnly]
    serializer_class = UserSubscribtionsSerializer

    def list(self, request):
        recipes_limit = int(request.GET.get(
            'recipes_limit', DEFAULT_RECIPE_LIMIT
        ))
        user = request.user
        authors = Subscribe.objects.select_related('author').filter(user=user)
        queryset = User.objects.filter(pk__in=authors.values('author_id'))
        page = self.paginate_queryset(queryset)
        serializer = UserSubscribtionsSerializer(page, many=True, context={
            'queryset': queryset,
            'user': user,
            'recipes_limit': recipes_limit
        }
        )
        return self.get_paginated_response(serializer.data)