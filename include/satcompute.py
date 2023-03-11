import math
import numpy as np
from include import Satellite_class
from include import GroundStation_class
from include import Observation_class
from include.SimParameter_class import SimParameter
from typing  import Union


# input：1.sat radius 2.right ascension of ascending node 3.(omega+f) 4.inclination of sat
# output：current sat Right ascension
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
    M = (sat.n_o * t + sat.M_o) % (2 * math.pi)  # mean anomaly in time t
    f = M  # if circular orbit
    r = sat.a_o  # if circular orbit
    u = sat.omega_o + f
    alpha = sat_alpha(r, sat.Omega_o, u, sat.i_o)
    delta = math.asin(math.sin(u) * math.sin(sat.i_o))
    phi = delta  # lat in time t
    lam = alpha - (math.radians(SimParameter.get_start_greenwich()) + Satellite_class.omega_e * t) % (2 * math.pi)  # lon in time t
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


# get tge phi range of ground
# input：1. r of sat 2.lat_rad of ground(ground station/obervation point)
# output：1.phi_min 2.phi_max
def get_sat_phi_range(r, lat_rad):
    temp = r * math.sin(SimParameter.get_off_nadir()) / Satellite_class.Re
    if temp <= 1:
        psi = math.asin(temp) - SimParameter.get_off_nadir()
    else:
        psi = math.acos(Satellite_class.Re / r)
    phi_min = max(lat_rad - psi, -math.pi / 2)
    phi_max = min(lat_rad + psi, math.pi / 2)
    return phi_min, phi_max


# input：   1.phi_min 2.phi_max 3.sat
# output:   1.time window1 start t_min1
#           2.time window1 end t_max1
#           3.time window2 start t_min2
#           4.time window2 end t_max2
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

    t_min1 = (u_min1 - sat.omega_o - sat.M_o) / sat.n_o
    t_max1 = (u_max1 - sat.omega_o - sat.M_o) / sat.n_o
    t_min2 = (u_max2 - sat.omega_o - sat.M_o) / sat.n_o
    t_max2 = (u_min2 - sat.omega_o - sat.M_o) / sat.n_o
    return t_min1, t_max1, t_min2, t_max2

def sat_original_delay(gd:Observation_class.Observation, sat: Satellite_class.Satellite, gs: GroundStation_class.GroundStation):
    phi_min, phi_max = get_sat_phi_range(sat.a_o, gd.lat_rad)
    gd_t_min1, gd_t_max1, gd_t_min2, gd_t_max2 = get_sat_alpha_range(phi_min, phi_max, sat)

    # time window of gs
    phi_min, phi_max = get_sat_phi_range(sat.a_o, gs.lat_rad)
    gs_t_min1, gs_t_max1, gs_t_min2, gs_t_max2 = get_sat_alpha_range(phi_min, phi_max, sat)

    if gd_t_min1 < gs_t_min1:
        time_delay = gs_t_min1 - gd_t_min1
    elif gd_t_min1 < gs_t_max1:
        for i in np.arange(gs_t_min1, gs_t_max1+0.01, 0.01):
            if i > gd_t_min1:
                time_delay = gs_t_max1 - gd_t_min1
                break

    elif gd_t_min1 < gs_t_min2:
        time_delay = gs_t_min2 - gd_t_min1
    elif gd_t_min1 < gs_t_max2:
        for i in np.arange(gs_t_min1, gs_t_max2+0.01, 0.01):
            if i > gd_t_min1:
                time_delay = gs_t_max2 - gd_t_min1
                break

    elif gd_t_min2 < gs_t_min1:
        time_delay = gs_t_min1 - gd_t_min2
    elif gd_t_min2 < gs_t_max1:
        for i in np.arange(gs_t_min1, gs_t_max1+0.01, 0.01):
            if i > gd_t_min2:
                time_delay = gs_t_max1 - gd_t_min2
                break

    elif gd_t_min2 < gs_t_min2:
        time_delay = gs_t_min2 - gd_t_min2
    elif gd_t_min2 < gs_t_max2:
        for i in np.arange(gs_t_min1, gs_t_max2+0.05, 0.05):
            if i > gd_t_min2:
                time_delay = gs_t_max2 - gd_t_min2
                break

    else:
        return -1
    
    return time_delay