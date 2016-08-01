from django.contrib.gis.db import models as gis_models


class LocationMixin(object):
    location = gis_models.PointField()
