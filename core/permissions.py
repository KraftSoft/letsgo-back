import logging
import operator
from rest_framework.permissions import BasePermission, IsAuthenticated

logger = logging.getLogger(__name__)


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True


class IsStaffOrOwner(BasePermission):
    def has_permission(self, request, view):

        if request.user.is_anonymous():
            return False

        object_model = view.model

        if request.user.is_superuser:
            return True

        try:
            model = object_model.objects.get(pk=view.kwargs['pk'])
        except (object_model.DoesNotExist, KeyError):
            logger.exception('User can not update data')
            return False

        try:
            owner_pk = operator.attrgetter(view.path_to_owner_pk)(model)
        except AttributeError:
            logger.error('Wrong path tp owner')
            return False

        if request.user.pk == owner_pk:
            return True

        return False


class GeneralPermissionMixin(object):
    def get_permissions(self):

        if self.request.method == 'DELETE':
            return [self.who_can_update()]

        elif self.request.method == 'GET':  # only authorized users can see objects
            return [IsAuthenticated()]

        elif self.request.method == 'POST':  # only authorized users can create objects
            return [IsAuthenticated()]

        elif self.request.method == 'PUT':
            return [self.who_can_update()]  # only owners can update objects
        else:
            return [lambda: False]
