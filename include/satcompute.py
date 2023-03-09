import math
from include import Satellite_class
from include import GroundStation_class
from include import Observation_class
from include.SimParameter_class import SimParameter
from typing  import Union

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


def get_sat_eci_xyz(t, sat: Satellite_class.Satellite):
    u = sat.omega_o + (sat.n_o * t + sat.M_o) % (2 * math.pi)
    alpha = sat_alpha(sat.r, sat.Omega_o, u, sat.i_o) # right ascension
    delta = math.asin(math.sin(u) * math.sin(sat.i_o))  # in time t

    x = sat.r * math.cos(delta) * math.cos(alpha)
    y = sat.r * math.cos(delta) * math.sin(alpha)
    z = sat.r * math.sin(delta)

    return (x, y, z)


def get_ground_eci_xyz(t, ground: Union[GroundStation_class.GroundStation, Observation_class.Observation]):
    u = (math.radians(SimParameter.get_start_greenwich()) + ground.lon_rad) % (2 * math.pi)
    alpha = (u + Satellite_class.omega_e * t) % (2 * math.pi)

    x = Satellite_class.Re * math.cos(ground.lat_rad) * math.cos(alpha)
    y = Satellite_class.Re * math.cos(ground.lat_rad) * math.sin(alpha)
    z = Satellite_class.Re * math.sin(ground.lat_rad)

    return (x, y, z)


# input     1. t (time passed from start_greenwich, in sec)
#           2. sat_1 (first satellite)
#           3. sat_2 (first satellite)
def inter_sat_distance(t, sat_1: Satellite_class.Satellite, sat_2: Satellite_class.Satellite):
    from_x, from_y, from_z = get_sat_eci_xyz(t, sat_1)

    to_x, to_y, to_z = get_sat_eci_xyz(t, sat_2)
    
    return ((from_x - to_x)**2 + (from_y - to_y)**2 + (from_z - to_z)**2) **(1/2)


# input     1. t (time passed from start_greenwich, in sec)
#           2. sat_1 (Satellite)
#           3. gs (Ground Station)
def sat_ground_distance(t, sat: Satellite_class.Satellite, gs: GroundStation_class.GroundStation):
    from_x, from_y, from_z = get_sat_eci_xyz(t, sat)

    to_x, to_y, to_z = get_ground_eci_xyz(t, gs)

    return math.sqrt((from_x - to_x)**2 + (from_y - to_y)**2 + (from_z - to_z)**2)


# 根据给定的最大off_nadir角和地面点，求卫星可能观测到的纬度带
# 输入：1.最大off_nadir角 2.卫星半径 3.地面点纬度
# 输出：1.卫星与地心的连线和地面点与地心的连线之间最大的可视夹角 2.纬度带最小值 3.纬度带最大值
def get_sat_phi_range(r, lat_rad):
    temp = r * math.sin(SimParameter.get_off_nadir()) / Satellite_class.Re
    if temp <= 1:
        psi = math.asin(temp) - SimParameter.get_off_nadir()
    else:
        psi = math.acos(Satellite_class.Re / r)
    phi_min = max(lat_rad - psi, -math.pi / 2)
    phi_max = min(lat_rad + psi, math.pi / 2)
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
