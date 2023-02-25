from api.pagination import LimitPageNumberPagination
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from .models import Subscribe, User
from .serializers import CustomUserSerializer, SubscribeSerializer, SubscribeListSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = LimitPageNumberPagination

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = self.request.user
        queryset = User.objects.filter(following__user=user)
        if queryset:
            pages = self.paginate_queryset(queryset)
            serializer = SubscribeListSerializer(
                pages,
                many=True,
                context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(
            'Вы ни на кого не подписаны',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            context = {'request': request}
            data = {
                'user': user.id,
                'author': author.id
            }
            serializer = SubscribeSerializer(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        subscribe = get_object_or_404(
            Subscribe,
            user=user,
            author=author
        )
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)