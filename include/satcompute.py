import numpy as np
import math
from include import Satellite_class
from include import GroundStation_class
from astropy.time import Time
from astropy import units as u
from pyproj import CRS, Transformer
from include.SimParameter_class import SimParameter

# 根据轨道六要素求卫星当前位置赤经
# 输入：1.卫星半径 2.升交点赤经 3.卫星轨道面上卫星当前位置与升交点赤经的角度(omega+f) 4.轨道倾角
# 输出：卫星当前位置赤经
def sat_alpha(r, Omega_o, u, i_o):
    x = r * (math.cos(Omega_o) * math.cos(u) - math.sin(Omega_o) * math.sin(u) * math.cos(i_o))
    y = r * (math.sin(Omega_o) * math.cos(u) + math.cos(Omega_o) * math.sin(u) * math.cos(i_o))
    if y > 0:
        if x > 0:
            s_alpha = math.atan(y / x)
        elif x < 0:
            s_alpha = math.atan(y / x) + math.pi
    if y < 0:
        if x > 0:
            s_alpha = math.atan(y / x) + 2 * math.pi
        elif x < 0:
            s_alpha = math.atan(y / x) + math.pi
    if y == 0:
        if x > 0:
            s_alpha = 0
        elif x < 0:
            s_alpha = math.pi
    if x == 0:
        if y > 0:
            s_alpha = math.pi / 2
        elif y < 0:
            s_alpha = 3 * math.pi / 2
    return s_alpha


# input     1. sat (Satellite Class Object)
#           2. t (time passed from start_greenwich, in sec)
def get_sat_lat_lon(sat: Satellite_class.Satellite, t):
    M = (sat.n_o * t + sat.M_o) % (2 * math.pi)  # t时刻平近点角(rad)
    f = M  # if circular orbit
    r = sat.a_o  # if circular orbit
    u = sat.omega_o + f
    alpha = sat_alpha(r, sat.Omega_o, u, sat.i_o)
    delta = math.asin(math.sin(u) * math.sin(sat.i_o))  # t时刻卫星赤纬
    phi = delta  # t时刻卫星地心纬度, lat
    lam = alpha - (math.radians(SimParameter.get_start_greenwich()) + Satellite_class.omega_e * t) % (2 * math.pi)  # t时刻卫星地心经度, lon
    if lam > math.pi:
        lam = lam - 2 * math.pi
    if lam < -math.pi:
        lam = lam + 2 * math.pi

    return phi, lam


# input     1. t (time passed from start_greenwich, in sec)
#           2. sat_1 (first satellite)
#           3. sat_2 (first satellite)
def inter_sat_distance(t, sat_1: Satellite_class.Satellite, sat_2: Satellite_class.Satellite):
    from_u = sat_1.omega_o + (sat_1.n_o * t + sat_1.M_o) % (2 * math.pi)
    from_alpha = sat_alpha(sat_1.r, sat_1.Omega_o, from_u, sat_1.i_o) # right ascension
    from_delta = math.asin(math.sin(from_u) * math.sin(sat_1.i_o))  # in time t

    from_x = sat_1.r * math.cos(from_delta) * math.cos(from_alpha)
    from_y = sat_1.r * math.cos(from_delta) * math.sin(from_alpha)
    from_z = sat_1.r * math.sin(from_delta)

    to_u = sat_2.omega_o + (sat_2.n_o * t + sat_2.M_o) % (2 * math.pi)
    to_alpha = sat_alpha(sat_2.r, sat_2.Omega_o, to_u, sat_2.i_o)   # right ascension in time t
    to_delta = math.asin(math.sin(to_u) * math.sin(sat_2.i_o))  # declination in time t

    to_x = sat_2.r * math.cos(to_delta) * math.cos(to_alpha)
    to_y = sat_2.r * math.cos(to_delta) * math.sin(to_alpha)
    to_z = sat_2.r * math.sin(to_delta)
    
    return ((from_x - to_x)**2 + (from_y - to_y)**2 + (from_z - to_z)**2) **(1/2)


# def eci_from_latlon(t, gs):
#     # Convert latitude and longitude to degrees
#     lat_deg = math.degrees(gs.lat_rad)
#     lon_deg = math.degrees(gs.lon_rad)

#     if lon_deg > 180:
#         lon_deg -= 360
        
#     # print(lat_deg, lon_deg, gs.lat_rad, gs.lon_rad)

#     # Calculate the current GMST in radians
#     current_gmst_rad = SimParameter.get_start_greenwich() + (1.00273790935 * t) % (2 * np.pi)

#     # Calculate the transformation matrix from ECEF to ECI coordinates
#     c = np.cos(current_gmst_rad)
#     s = np.sin(current_gmst_rad)
#     T = np.array([
#         [-s, c, 0],
#         [-c, -s, 0],
#         [0, 0, 1]
#     ])

#     #  Define the WGS84 ellipsoid using a Proj string
#     ellps_proj_str = "+ellps=WGS84 +a=6378137 +rf=298.257223563"

#     # Create a transformer object to convert lat/lon to ECEF coordinates
#     transformer = Transformer.from_crs(
#         CRS.from_proj4("+proj=longlat +ellps=WGS84"),
#         CRS.from_proj4("+proj=geocent " + ellps_proj_str)
#     )

#     # Convert the lat/lon coordinates to ECEF coordinates
#     ecef_x, ecef_y, ecef_z = transformer.transform(gs.lon_rad, gs.lat_rad, 0, radians=True)

#     # Apply the transformation matrix to convert ECEF to ECI coordinates
#     eci_coords = T @ np.array([ecef_x, ecef_y, ecef_z])

#     return eci_coords[0], eci_coords[1], eci_coords[2]



# input     1. t (time passed from start_greenwich, in sec)
#           2. sat_1 (Satellite)
#           3. gs (Ground Station)
def sat_ground_distance(t, sat: Satellite_class.Satellite, gs: GroundStation_class.GroundStation):
    from_u = sat.omega_o + (sat.n_o * t + sat.M_o) % (2 * math.pi)
    from_alpha = sat_alpha(sat.r, sat.Omega_o, from_u, sat.i_o) # right ascension
    from_delta = math.asin(math.sin(from_u) * math.sin(sat.i_o))  # in time t

    from_x = sat.r * math.cos(from_delta) * math.cos(from_alpha)
    from_y = sat.r * math.cos(from_delta) * math.sin(from_alpha)
    from_z = sat.r * math.sin(from_delta)

    to_u = (math.radians(SimParameter.get_start_greenwich()) + gs.lon_rad) % (2 * math.pi)
    to_alpha = (to_u + Satellite_class.omega_e * t) % (2 * math.pi)

    # temp_x, temp_y, temp_z = eci_from_latlon(t, gs)
    to_x = Satellite_class.Re * math.cos(gs.lat_rad) * math.cos(to_alpha)
    to_y = Satellite_class.Re * math.cos(gs.lat_rad) * math.sin(to_alpha)
    to_z = Satellite_class.Re * math.sin(gs.lat_rad)

    return math.sqrt((from_x - to_x)**2 + (from_y - to_y)**2 + (from_z - to_z)**2)


# 根据给定的最大off_nadir角和地面点，求卫星可能观测到的纬度带
# 输入：1.最大off_nadir角 2.卫星半径 3.地面点纬度
# 输出：1.卫星与地心的连线和地面点与地心的连线之间最大的可视夹角 2.纬度带最小值 3.纬度带最大值
def get_sat_phi_range(off_nadir, r, gd_lat_rad):
    temp = r * math.sin(off_nadir) / Satellite_class.Re
    if temp <= 1:
        psi = math.asin(temp) - off_nadir
    else:
        psi = math.acos(Satellite_class.Re / r)
    phi_min = max(gd_lat_rad - psi, -math.pi / 2)
    phi_max = min(gd_lat_rad + psi, math.pi / 2)
    return psi, phi_min, phi_max


# 求卫星到达可能观测到的纬度带的赤经范围，以及到达时刻
# 输入：1.纬度带最小值 2.纬度带最大值 3.卫星class
# 输出：由于卫星轨道与纬度带有两个交叉范围，因此会求出两个赤经范围(特殊情况就是两个赤经范围刚好连上)
#      1.第一个赤经范围：卫星纬度到达纬度带最小值时的赤经 alpha_min1
#      2.第一个赤经范围：卫星纬度到达纬度带最大值时的赤经 alpha_max1
#      3.第二个赤经范围：卫星纬度到达纬度带最小值时的赤经 alpha_min2
#      4.第二个赤经范围：卫星纬度到达纬度带最大值时的赤经 alpha_max2
#      5.卫星到达alpha_min1对应的时刻 t_min1 (相对于simulate开始时刻；t_min1+kT   k为整数，T为卫星周期)
#      6.卫星到达alpha_max1对应的时刻 t_max1
#      7.卫星到达alpha_min2对应的时刻 t_min2
#      8.卫星到达alpha_max2对应的时刻 t_max2
def get_sat_alpha_range(phi_min, phi_max, sat: Satellite_class.Satellite):
    sin_u_min1 = math.sin(phi_min) / math.sin(sat.i_o)
    sin_u_max1 = math.sin(phi_max) / math.sin(sat.i_o)
    if abs(sin_u_min1) <= 1:
        u_min1 = math.asin(sin_u_min1)
    else:
        u_min1 = math.pi / 2
    if abs(sin_u_max1) <= 1:
        u_max1 = math.asin(sin_u_max1)
    else:
        u_max1 = math.pi / 2
    u_max2 = math.pi - u_max1
    u_min2 = math.pi - u_min1

    alpha_min1 = sat_alpha(sat.r, sat.Omega_o, u_min1, sat.i_o)
    alpha_max1 = sat_alpha(sat.r, sat.Omega_o, u_max1, sat.i_o)
    alpha_min2 = sat_alpha(sat.r, sat.Omega_o, u_min2, sat.i_o)
    alpha_max2 = sat_alpha(sat.r, sat.Omega_o, u_max2, sat.i_o)

    t_min1 = (u_min1 - sat.omega_o - sat.M_o) / sat.n_o
    t_max1 = (u_max1 - sat.omega_o - sat.M_o) / sat.n_o
    t_min2 = (u_max2 - sat.omega_o - sat.M_o) / sat.n_o
    t_max2 = (u_min2 - sat.omega_o - sat.M_o) / sat.n_o
    return alpha_min1, alpha_max1, alpha_min2, alpha_max2, t_min1, t_max1, t_min2, t_max2


# 求地面点可能被卫星看到的赤经范围，即只有地面点进入该范围，才有可能被卫星观测到
# 输入：1.卫星与地心的连线和地面点与地心的连线之间最大的可视夹角 psi
#      2.纬度带最小值
#      3.纬度带最大值
#      4.轨道倾角
#      5.第一个赤经范围：卫星纬度到达纬度带最小值时的赤经 alpha_min1
#      6.第一个赤经范围：卫星纬度到达纬度带最大值时的赤经 alpha_max1
#      7.第二个赤经范围：卫星纬度到达纬度带最小值时的赤经 alpha_min2
#      8.第二个赤经范围：卫星纬度到达纬度带最大值时的赤经 alpha_max2
# 输出：1.是否地面点在整个赤经范围内都可能被观测到（这在地面点近极点时可能发生）
#      2.地面点的赤经范围[gd_rang_of_alpha1, gd_rang_of_alpha2]
def get_observation_alpha_range(psi, phi_min, phi_max, i_o, alpha_min1, alpha_max1, alpha_min2, alpha_max2):
    cos_theta_fin = (math.cos(psi) - math.sin(phi_min) ** 2) / (math.cos(phi_min) ** 2)
    cos_theta_fax = (math.cos(psi) - math.sin(phi_max) ** 2) / (math.cos(phi_max) ** 2)
    # phi_min对应的最大theta值
    all_seen = 0
    if abs(cos_theta_fin) <= 1:
        theta_fin = math.acos(cos_theta_fin)
    else:
        all_seen = 1
        theta_fin = math.pi
    # phi_max对应的最大theta值
    if abs(cos_theta_fax) <= 1:
        theta_fax = math.acos(cos_theta_fax)
    else:
        all_seen = 1
        theta_fax = math.pi
    # 正飞和逆飞的不同情况讨论
    if i_o <= math.pi / 2:  # 正飞
        gd_rang_of_alpha1 = [(alpha_min1 - theta_fin) % (2 * math.pi), (alpha_max1 + theta_fax) % (2 * math.pi)]
        gd_rang_of_alpha2 = [(alpha_max2 - theta_fax) % (2 * math.pi), (alpha_min2 + theta_fin) % (2 * math.pi)]
    else:  # 逆飞
        gd_rang_of_alpha1 = [(alpha_max1 - theta_fax) % (2 * math.pi), (alpha_min1 + theta_fin) % (2 * math.pi)]
        gd_rang_of_alpha2 = [(alpha_min2 - theta_fin) % (2 * math.pi), (alpha_max2 + theta_fax) % (2 * math.pi)]
    return all_seen, gd_rang_of_alpha1, gd_rang_of_alpha2
