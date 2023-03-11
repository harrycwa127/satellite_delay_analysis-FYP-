# the ground station
class GroundStation(object):
    lat_rad = 0         # latitude (rad)
    lon_rad = 0         # longitude (rad)
    ele_rad = 0         # elevation

    def __init__(self, lat_rad, lon_rad, ele_rad):
        self.lat_rad = lat_rad
        self.lon_rad = lon_rad
        self.ele_rad = ele_rad

    def __str__(self):
        return "lat: %s; long: %s; ele: %s" % (self.lat_rad, self.lon_rad, self.ele_rad)

