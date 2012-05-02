# nhlib: A New Hazard Library
# Copyright (C) 2012 GEM Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Module :mod:`nhlib.geo.point` defines :class:`Point`.
"""
from nhlib.geo._utils import EARTH_RADIUS, ensure
from nhlib.geo import geodetic


class Point(object):
    """
    This class represents a geographical point in terms of
    longitude, latitude, and depth (with respect to the Earth surface).

    :param longitude:
        Point longitude, in decimal degrees.
    :type longitude:
        float
    :param latitude:
        Point latitude, in decimal degrees.
    :type latitude:
        float
    :param depth:
        Point depth (default to 0.0), in km. Depth > 0 indicates a point
        below the earth surface, and depth < 0 above the earth surface.
    :type depth:
        float
    """
    #: The distance between two points for them to be considered equal,
    #: in km.
    EQUALITY_DISTANCE = 1e-3

    def __init__(self, longitude, latitude, depth=0.0):

        ensure(depth < EARTH_RADIUS,
                "The depth must be < than the earth radius (6371.0 km)!")

        ensure(-180.0 <= longitude <= 180.0,
                "Longitude %.6f outside range!" % longitude)

        ensure(-90.0 <= latitude <= 90.0,
                "Latitude %.6f outside range!" % latitude)

        self.depth = depth
        self.latitude = latitude
        self.longitude = longitude

    def point_at(self, horizontal_distance, vertical_increment, azimuth):
        """
        Compute the point with given horizontal, vertical distances
        and azimuth from this point.

        :param horizontal_distance:
            Horizontal distance, in km.
        :type horizontal_distance:
            float
        :param vertical_increment:
            Vertical increment, in km. When positive, the new point
            has a greater depth. When negative, the new point
            has a smaller depth.
        :type vertical_increment:
            float
        :type azimuth:
            Azimuth, in decimal degrees.
        :type azimuth:
            float
        :returns:
            The point at the given distances.
        :rtype:
            Instance of :class:`Point`
        """
        lons, lats, depths = geodetic.npoints_towards(
            self.longitude, self.latitude, self.depth,
            azimuth, horizontal_distance, vertical_increment, 2
        )
        return Point(lons[1], lats[1], depths[1])

    def azimuth(self, point):
        """
        Compute the azimuth (in decimal degrees) between this point
        and the given point.

        :param point:
            Destination point.
        :type point:
            Instance of :class:`Point`
        :returns:
            The azimuth, value in a range ``[0, 360)``.
        :rtype:
            float
        """
        return geodetic.azimuth(self.longitude, self.latitude,
                                point.longitude, point.latitude)

    def distance(self, point):
        """
        Compute the distance (in km) between this point and the given point.

        Distance is calculated using pythagoras theorem, where the
        hypotenuse is the distance and the other two sides are the
        horizontal distance (great circle distance) and vertical
        distance (depth difference between the two locations).

        :param point:
            Destination point.
        :type point:
            Instance of :class:`Point`
        :returns:
            The distance.
        :rtype:
            float
        """
        return geodetic.distance(self.longitude, self.latitude, self.depth,
                                 point.longitude, point.latitude, point.depth)

    def __str__(self):
        """
        >>> str(Point(1, 2, 3))
        '<Latitude=2.000000, Longitude=1.000000, Depth=3.0000>'
        >>> str(Point(1.0 / 3.0, -39.999999999, 1.6666666666))
        '<Latitude=-40.000000, Longitude=0.333333, Depth=1.6667>'
        """
        return "<Latitude=%.6f, Longitude=%.6f, Depth=%.4f>" % (
                self.latitude, self.longitude, self.depth)

    def __repr__(self):
        """
        >>> str(Point(1, 2, 3)) == repr(Point(1, 2, 3))
        True
        """
        return self.__str__()

    def __eq__(self, other):
        """
        >>> Point(1e-4, 1e-4) == Point(0, 0)
        False
        >>> Point(1e-6, 1e-6) == Point(0, 0)
        True
        >>> Point(0, 0, 1) == Point(0, 0, 0)
        False
        >>> Point(4, 5, 1e-3) == Point(4, 5, 0)
        True
        >>> Point(-180 + 1e-7, 0) == Point(180 - 1e-7, 0)
        True
        """
        if other == None:
            return False
        return abs(self.distance(other)) <= self.EQUALITY_DISTANCE

    def __ne__(self, other):
        return not self.__eq__(other)

    def on_surface(self):
        """
        Check if this point is defined on the surface (depth is 0.0).

        :returns:
            True if this point is on the surface, false otherwise.
        :rtype:
            boolean
        """
        return self.depth == 0.0

    def equally_spaced_points(self, point, distance):
        """
        Compute the set of points equally spaced between this point
        and the given point.

        :param point:
            Destination point.
        :type point:
            Instance of :class:`Point`
        :param distance:
            Distance between points (in km).
        :type distance:
            float
        :returns:
            The list of equally spaced points.
        :rtype:
            list of :class:`Point` instances
        """
        lons, lats, depths = geodetic.intervals_between(
            self.longitude, self.latitude, self.depth,
            point.longitude, point.latitude, point.depth,
            distance
        )
        return [Point(lons[i], lats[i], depths[i]) for i in xrange(len(lons))]
