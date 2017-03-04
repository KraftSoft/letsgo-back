import logging
import operator

from rest_framework.permissions import BasePermission, IsAdminUser, IsAuthenticated

logger = logging.getLogger(__name__)


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True


class IsStaffOrTargetUser(IsStaff):
    def has_permission(self, request, view):

        if request.user.pk == view.kwargs.get('pk'):
            return True

        return super().has_permission(request, view)


class IsStaffOrOwner(BasePermission):
    def has_permission(self, request, view):

        if request.user.is_anonymous():
            return False

        object_model = view.model

        try:
            model = object_model.objects.get(pk=view.kwargs['pk'])
        except (object_model.DoesNotExist, KeyError):
            return False

        path_to_owner = getattr(view, 'owner_path', 'owner')

        try:
            owner = operator.attrgetter(path_to_owner)(model)
        except AttributeError:
            logger.error('Wrong path tp owner')
            return False

        if request.user.pk == owner.pk:
            return True

        return super().has_permission(request, view)


class IsStaffOrMe(BasePermission):
    def has_permission(self, request, view):
        me = view.model
        if request.user.pk == me.pk:
            return True
        return super().has_permission(request, view)


class GeneralPermissionMixin(object):
    def get_permissions(self):

        if self.request.method == 'DELETE':
            return [IsAdminUser()]

        elif self.request.method == 'GET':  # only authorized users can see objects
            return [IsAuthenticated()]

        elif self.request.method == 'POST':  # only authorized users can create objects
            return [IsAuthenticated()]

        else:
            return [self.who_can_update()]  # only owners can update objects
