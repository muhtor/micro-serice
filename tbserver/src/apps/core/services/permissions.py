from django.shortcuts import redirect
from django.contrib.auth.mixins import AccessMixin
from apps.core.services.model_status import UserType
from rest_framework import permissions


class AdminRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and user is is_superuser."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # must be the owner to view the object
        return obj.user == request.user


class UserIsCustomer(permissions.BasePermission):
    """
    Return `True` if permission is granted, `False` otherwise.
    """
    message = 'accepted only customer users'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            is_customer = False
            if request.user.type == UserType.CUSTOMER:
                is_customer = True
            return bool(is_customer)
        return False


class UserIsExecutor(permissions.BasePermission):
    """
    Return `True` if permission is granted, `False` otherwise.
    """
    message = 'accepted only driver users'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            is_driver = False
            if request.user.type == UserType.DRIVER:
                is_driver = True
            return bool(is_driver)
        return False


class UserIsAgent(permissions.BasePermission):
    """
    Return `True` if permission is granted, `False` otherwise.
    """
    message = 'accepted only agent users'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            is_agent = False
            if request.user.type == UserType.AGENT:
                is_agent = True
            return bool(is_agent)
        return False


class UserIsCustomerOrIsExecutor(permissions.BasePermission):
    """
    Return `True` if permission is granted, `False` otherwise.
    """
    message = 'accepted only customer or driver users'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                is_allowed = True
            elif request.user.type == UserType.CUSTOMER or request.user.type == UserType.DRIVER:
                is_allowed = True
            else:
                is_allowed = False
            return is_allowed
        return False


class UserIsAgentOrIsExecutor(permissions.BasePermission):
    """
    Return `True` if permission is granted, `False` otherwise.
        (1, "Customer"),
        (2, "Agent"),
        (3, "Driver"),
        (4, "Merchant"),
        (5, "MerchantUser"),
        (6, "Admin"),
    """
    message = 'accepted only agent or driver users'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                is_allowed = True
            elif request.user.type == UserType.AGENT or request.user.type == UserType.DRIVER:
                is_allowed = True
            else:
                is_allowed = False
            return is_allowed
        return False