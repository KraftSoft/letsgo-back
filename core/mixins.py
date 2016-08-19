from django.contrib.gis.db import models as gis_models
from django.db import models


class LocationMixin(models.Model):
    coordinates = gis_models.PointField(null=True, blank=False)

    class Meta:
        abstract = True


class WriteMixin(object):

    m2m_fields = tuple()
    fk_fields = tuple()

    def add_m2m_field(self, instance, attr, value):
        raise NotImplementedError

    def add_fk_field(self, instance, attr, value):
        raise NotImplementedError

    def add_field(self, instance, attr, value):
        if attr in self.m2m_fields:
            self.add_m2m_field(instance, attr, value)
        elif attr in self.fk_fields:
            self.add_fk_field(instance, attr, value)
        else:
            setattr(instance, attr, value)
