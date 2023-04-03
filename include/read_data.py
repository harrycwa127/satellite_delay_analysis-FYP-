from include import greenwich
from include import Observation_class
from include import GroundStation_class

import math

def get_start_julian_time():
    time_f = open('settings/TIME_INTERVAL.txt', 'r')
    time_lines = []
    for line in time_f.readlines():
        time_lines.append(line.split())
    start_time_julian = greenwich.julian(int(time_lines[0][0]), int(time_lines[0][1]), int(time_lines[0][2]),
                                        int(time_lines[0][3]), int(time_lines[0][4]), int(time_lines[0][5]))
    start_greenwich = (greenwich.greenwich(start_time_julian)) % 360   # from 0 degree to 360 degree

    return (start_time_julian, start_greenwich)

def get_observation():
    gd_lines = []
    obs_f = open('settings/test_OBSERVATION.txt', 'r')
    for line in obs_f.readlines():
        gd_lines.append(line.split(' '))
    obs_f.close()
    gd_accounts = len(gd_lines)
    gd_list = []
    for g in range(gd_accounts):
        region_lat = float(gd_lines[g][0])
        region_long = float(gd_lines[g][1])
        
        if region_long < 0:
            region_long = 360 + region_long
        if region_lat < 0:
            region_lat = 360 + region_lat

        region_lat_rad = math.radians(region_lat)       # rad
        region_lon_rad = math.radians(region_long)     # rad
        gd = Observation_class.Observation(region_lat_rad, region_lon_rad)
        gd_list.append(gd)

    return gd_list

def get_observation2():
    gd_lines = []
    obs_f = open('settings/main_OBSERVATION.txt', 'r')
    for line in obs_f.readlines():
        gd_lines.append(line.split(' '))
    obs_f.close()
    region_lat = float(gd_lines[0][0])
    region_long = float(gd_lines[0][1])

    if region_long < 0:
        region_long = 360 + region_long
    if region_lat < 0:
        region_lat = 360 + region_lat

    region_lat_rad = math.radians(region_lat)       # rad
    region_lon_rad = math.radians(region_long)     # rad
    gd = Observation_class.Observation(region_lat_rad, region_lon_rad)

    return gd

def get_select_gs():
    gs_lines = []
    input_f2 = open('settings/test_GROUND_STATION.txt', 'r')
    for line in input_f2.readlines():
        tmpl = line.strip()
        gs_lines.append(tmpl.split(' '))
    input_f2.close()
    gs_accounts = len(gs_lines)
    gs_list = []
    for g in range(gs_accounts):
        gs_lat = float(gs_lines[g][0])
        gs_long = float(gs_lines[g][1])
        if gs_long < 0:
            gs_long = 360 + gs_long
        if gs_lat < 0:
            gs_lat = 360 + gs_lat
        gs_ele = 10
        gs_lat_rad = math.radians(gs_lat)  # rad
        gs_lon_rad = math.radians(gs_long)  # rad
        gs_ele_rad = math.radians(gs_ele)  # rad
        gs = GroundStation_class.GroundStation(gs_lat_rad, gs_lon_rad, gs_ele_rad)
        gs_list.append(gs)

    return gs_list

def get_gs():
    gs_lines = []
    input_f2 = open('settings/main_GROUND_STATION.txt', 'r')
    for line in input_f2.readlines():
        tmpl = line.strip()
        gs_lines.append(tmpl.split(' '))
    input_f2.close()

    gs_lat = float(gs_lines[0][0])
    gs_long = float(gs_lines[0][1])
    if gs_long < 0:
        gs_long = 360 + gs_long
    if gs_lat < 0:
        gs_lat = 360 + gs_lat
    gs_ele = float(gs_lines[0][2])
    # gs_ele = 10
    gs_lat_rad = math.radians(gs_lat)  # rad
    gs_lon_rad = math.radians(gs_long)  # rad
    gs_ele_rad = math.radians(gs_ele)  # rad
    gs = GroundStation_class.GroundStation(gs_lat_rad, gs_lon_rad, gs_ele_rad)

    return gs