# /backend/api/views/users.py:
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.paginations import CustomPagination
from api.serializers import (CustomUserSerializer,
                             SubscribeCreateDeleteSerializer)
from users.models import CustomUser, Subscription


class UsersViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination
    http_method_names = ["get", "post", "delete", "head"]

    def get_permissions(self):
        if self.action == "me":
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(
        methods=["POST", "DELETE"],
        detail=True,
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        serializer = SubscribeCreateDeleteSerializer(
            author, context={"request": request}
        )

        if request.method == "POST":
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            subscription = Subscription.objects.filter(
                user=user, author=author
            )
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"error": "Вы не подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        authors = CustomUser.objects.filter(subscribers__user=user)
        page = self.paginate_queryset(authors)
        serializer = SubscribeCreateDeleteSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
