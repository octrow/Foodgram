from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAdminUser)


class ActiveUserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_active


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.owner == request.user


class AuthorAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return ActiveUserPermission().has_permission(request, view) and (
            IsAdminUser() | IsOwnerOrReadOnly()
        ).has_object_permission(request, view, obj)
