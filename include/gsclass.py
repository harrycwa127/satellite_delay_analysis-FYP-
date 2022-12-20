# the ground station
class GS(object):
    lat_rad = 0      # latitude (rad)
    long_rad = 0     # longitude (rad)
    ele_rad = 0      # elevation

    def __init__(self, lat_rad, long_rad, ele_rad):
        self.lat_rad = lat_rad
        self.long_rad = long_rad
        self.ele_rad = ele_rad

    def __str__(self):
        return "lat: %s; long: %s; ele: %s" % (self.lat_rad, self.long_rad, self.ele_rad)

