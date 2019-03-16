from django.contrib.gis.geos.point import Point


def get_center_of_points(points):
    """ calculate the weighted center of a given set of points """
    if points:
        points = tuple(points)
        # all points must use the same projection
        assert len(set(point.get_srid() for point in points)) == 1
        result = Point(sum(point.x for point in points) / len(points),
                       sum(point.y for point in points) / len(points))
        result.set_srid(points[0].get_srid())
        return result
    else:
        return None
