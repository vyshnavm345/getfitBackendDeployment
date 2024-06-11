from rest_framework import permissions
# from rest_framework.permissions import BasePermission

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """

    def has_permission(self, request, view):
        # Check if the user making the request is an admin
        return request.user and request.user.is_authenticated and request.user.is_superuser
    
    

class IsNotBlocked(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated or not request.user.blocked