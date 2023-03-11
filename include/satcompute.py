import math
import numpy as np
from include import Satellite_class
from include import GroundStation_class
from include import Observation_class
from include import communication
from include import visibility
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


# input:    1. gd   2.sat   3. gs
# output:   time
def sat_original_delay(gd:Observation_class.Observation, sat: Satellite_class.Satellite, gs: GroundStation_class.GroundStation):
    t = 0
    if visibility.is_observation_visible(t, sat, gd) == False:
        # find time can commnicate with, in sec
        while visibility.is_observation_visible(t, sat, gd) == False:
            t += 1

        t -= 1
        while visibility.is_observation_visible(t, sat, gd) == False:
            t+=0.01
        
    
    # find time can commnicate with, in sec
    while visibility.is_gs_communicable(t, sat, gs) == False:
        t += 1

    # rollback 1 sec and find time in 0.01
    t -= 1
    while visibility.is_gs_communicable(t, sat, gs) == False:
        t+=0.01

    communication_end = False
    total_t = t
    while communication_end == False:
        temp = communication.sat_ground_commnicate(t, sat, gs)
        if temp > 0:
            t = temp
            communication_end = True
        else:
            t -= 0.001
            communication_end = False
            
            if total_t - t > 1:
                print("Satellite Orginal Communication Fail!!")
                return -1

    return t