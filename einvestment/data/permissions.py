from rest_framework.permissions import AllowAny, SAFE_METHODS, BasePermission


class IsLegal(BasePermission):
    message = 'Looking tables is restricted to the legal users only.'
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.is_active and not request.user.is_physic

