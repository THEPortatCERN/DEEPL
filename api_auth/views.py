from django.contrib.auth.models import User
from rest_framework import (
    filters,
    viewsets,
    permissions
)

from api_auth.serializers import UserSerializer


class UserPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method in ('POST', 'PUT', 'PATCH'):
            return request.user.is_superuser or obj == request.user
        return obj == request.user


class UserViewSet(viewsets.ModelViewSet):
    """
    create:
    Register a new user

    retrieve:
    Get an existing user

    list:
    Get a list of all users ordered by date joined

    destroy:
    Delete an existing user

    update:
    Modify an existing user

    partial_update:
    Modify an existing user partially
    """

    queryset = User.objects.filter(is_active=True).order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [UserPermission]

    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('username', 'first_name', 'last_name', 'email')

    def get_object(self):
        pk = self.kwargs['pk']
        if pk == 'me':
            return self.request.user
        else:
            return super().get_object()
