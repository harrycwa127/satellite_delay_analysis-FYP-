from include import gdclass
from include import gsclass
import math


def exclude_ground_station(gd: gdclass.GD, gs: gsclass.GS, max_rad):
    delta_phi = gd.lat_rad-gs.lat_rad
    delta_lam = gd.long_rad-gs.long_rad
    temp1 = math.sin(delta_phi/2)**2
    temp2 = math.cos(gd.lat_rad)*math.cos(gs.lat_rad)*math.sin(delta_lam/2)*math.sin(delta_lam/2)
    delta = 2*math.asin(math.sqrt(temp1+temp2))
    if delta > max_rad:
        return True
    return False

