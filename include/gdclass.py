# the observation point
class GD(object):
    lat_rad = 0      # latitude (rad)
    long_rad = 0     # longitude (rad)

    def __init__(self, lat_rad, long_rad):
        self.lat_rad = lat_rad
        self.long_rad = long_rad

    def __str__(self):
        return "lat: %s; long: %s" % (self.lat_rad, self.long_rad)

