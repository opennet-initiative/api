from django.contrib.gis.geos.point import Point


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
