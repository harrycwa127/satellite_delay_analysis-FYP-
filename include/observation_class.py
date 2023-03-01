# the observation point
class Observation(object):
    lat_rad = 0      # latitude (rad)
    lon_rad = 0     # longitude (rad)

    def __init__(self, lat_rad, lon_rad):
        self.lat_rad = lat_rad
        self.lon_rad = lon_rad

    def __str__(self):
        return "lat: %s; long: %s" % (self.lat_rad, self.lon_rad)

