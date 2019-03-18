import math

from django.conf import settings
from django.contrib.gis.geos.point import Point


BASE_SITE_RADIUS = getattr(settings, "BASE_SITE_RADIUS", 20)
MINIMUM_SITE_POPULATION = getattr(settings, "MINIMUM_SITE_POPULATION", 4)


def get_center_of_points(points):
    """ calculate the weighted center of a given set of points """
    points = tuple(points)
    if points:
        # all points must use the same projection
        assert len(set(point.srid for point in points)) == 1, \
                "Positions must share the same coordinate system: {}".format(points)
        result = Point(sum(point.x for point in points) / len(points),
                       sum(point.y for point in points) / len(points))
        result.srid = points[0].srid
        return result
    else:
        return None


def get_dynamic_site_radius(population_count):
    # Increase the radius based on the current population count in order to allow bigger sites.
    # The factor below keeps the target density (population per area) constant.
    population_factor = max(1, math.sqrt(population_count / MINIMUM_SITE_POPULATION))
    return BASE_SITE_RADIUS * population_factor
