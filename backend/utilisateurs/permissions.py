from rest_framework.permissions import BasePermission

class EstAdmin(BasePermission):
    """Autorise uniquement les utilisateurs avec role='admin'."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )