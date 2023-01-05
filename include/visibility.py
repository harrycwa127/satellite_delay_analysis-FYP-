from include import Satellite_class
from include import GroundStation_class
from include import satcompute
from include import observation_class
import math


# Determine whether the satellite can image the obervation point
# 输入：1.当前时刻t（相对于开始时刻的时间）
#      2.卫星class
#      3.地面点class
#      4.off_nadir角
#      5.开始时刻0经度所处的赤经
# 输出：TRUE OR FALSE
def is_visible(t, satellite: Satellite_class.Satellite, gd: observation_class.Observation, off_nadir, start_greenwich):
    phi, lam = satcompute.get_sat_geo_lat_lon(sat = satellite, t = t, start_greenwich = start_greenwich)

    theta = lam - gd.long_rad
    cos_psi = math.cos(gd.lat_rad) * math.cos(phi) * math.cos(theta) + math.sin(gd.lat_rad) * math.sin(phi)
    psi = math.acos(cos_psi)
    beta = math.atan(Satellite_class.Re * math.sin(psi) / (satellite.r - Satellite_class.Re * math.cos(psi)))  # off nadir angle, 注意atan得到的是[-pi/2,pi/2]
    if cos_psi > Satellite_class.Re / satellite.r and beta <= off_nadir:
        return True
    else:
        return False


# 判断当前时刻卫星是否能和地面站通信
# 输入：1.当前时刻t（相对于开始时刻的时间）
#      2.卫星class
#      3.地面站class
#      4.由地面站通信的最小仰角得到的最大的off_nadir角
#      4.开始时刻0经度所处的赤经
# 输出：TRUE OR FALSE
def is_gs_communicable(t, satellite: Satellite_class.Satellite, gs: GroundStation_class.GroundStation, gs_off_nadir, start_greenwich):
    phi, lam = satcompute.get_sat_geo_lat_lon(sat = satellite, t = t, start_greenwich = start_greenwich)
    
    theta = lam - gs.long_rad
    cos_psi = math.cos(gs.lat_rad) * math.cos(phi) * math.cos(theta) + math.sin(gs.lat_rad) * math.sin(phi)
    psi = math.acos(cos_psi)
    beta = math.atan(Satellite_class.Re * math.sin(psi) / (satellite.r - Satellite_class.Re * math.cos(psi)))  # off nadir angle, 注意atan得到的是[-pi/2,pi/2]

    if cos_psi > (Satellite_class.Re / satellite.r) and beta <= gs_off_nadir:
        return True
    else:
        return False

def is_sat_communicable(t, from_satellite: Satellite_class.Satellite, to_satellite: Satellite_class.Satellite):

    r3 = satcompute.sat_distance(t, from_satellite, to_satellite)

    beta = math.acos((r3**2 + from_satellite.r**2 - to_satellite.r**2) / (2 * r3 * from_satellite.r))

    off_nadir_limit = math.asin(Satellite_class.Re/from_satellite.r)

    if beta > off_nadir_limit:
        return True
    else:
        return False
