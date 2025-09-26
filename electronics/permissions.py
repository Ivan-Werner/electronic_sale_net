from rest_framework import permissions


class IsActiveEmployee(permissions.BasePermission):
    """Разрешение только для активных сотрудников"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active)


class IsActiveEmployeeOrReadOnly(permissions.BasePermission):
    """Разрешение на чтение - всем, на запись - активным сотрудникам"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_authenticated and request.user.is_active)
