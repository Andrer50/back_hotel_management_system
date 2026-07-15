from rest_framework.permissions import BasePermission


class IsStaffAuthenticated(BasePermission):
    """Permite acceso si el usuario está autenticado (personal de recepción)."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAdministrador(BasePermission):
    """Permite sólo a usuarios con role.name == 'Administrador'."""
    def has_permission(self, request, view):
        try:
            return bool(request.user and request.user.is_authenticated and request.user.role and request.user.role.name == 'Administrador')
        except Exception:
            return False
