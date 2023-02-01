from include import greenwich
from include import observation_class
from include import GroundStation_class

import math

def get_start_julian_time():
    time_f = open('settings/TIME_INTERVAL.txt', 'r')
    time_lines = []
    for line in time_f.readlines():
        time_lines.append(line.split())
    start_time_julian = greenwich.julian2(int(time_lines[0][0]), int(time_lines[0][1]), int(time_lines[0][2]),
                                        int(time_lines[0][3]), int(time_lines[0][4]), int(time_lines[0][5]))
    start_greenwich = (greenwich.greenwich(start_time_julian)) % 360   # from 0 degree to 360 degree

    return (start_time_julian, start_greenwich)

def get_start_end_time_interval():
    time_f = open('settings/TIME_INTERVAL.txt', 'r')
    time_lines = []
    for line in time_f.readlines():
        time_lines.append(line.split())
    start_time_julian = greenwich.julian2(int(time_lines[0][0]), int(time_lines[0][1]), int(time_lines[0][2]),
                                        int(time_lines[0][3]), int(time_lines[0][4]), int(time_lines[0][5]))
    end_time_julian = greenwich.julian2(int(time_lines[1][0]), int(time_lines[1][1]), int(time_lines[1][2]),
                                        int(time_lines[1][3]), int(time_lines[1][4]), int(time_lines[1][5]))
    time_interval = (end_time_julian-start_time_julian)*86400  # in sec
    start_greenwich = (greenwich.greenwich(start_time_julian)) % 360   # from 0 degree to 360 degree

    return (start_time_julian, start_greenwich, end_time_julian, time_interval)

def get_observation():
    gd_lines = []
    obs_f = open('settings/OBSERVATION.txt', 'r')
    for line in obs_f.readlines():
        gd_lines.append(line.split(' '))
    obs_f.close()
    gd_accounts = len(gd_lines)
    gd_list = []
    for g in range(gd_accounts):
        region_lat = float(gd_lines[g][0])
        region_long = float(gd_lines[g][1])
        region_lat_rad = math.radians(region_lat)       # rad
        region_long_rad = math.radians(region_long)     # rad
        gd = observation_class.Observation(region_lat_rad, region_long_rad)
        gd_list.append(gd)

    return gd_list

def get_observation2():
    gd_lines = []
    obs_f = open('settings/OBSERVATION2.txt', 'r')
    for line in obs_f.readlines():
        gd_lines.append(line.split(' '))
    obs_f.close()
    region_lat = float(gd_lines[0][0])
    region_long = float(gd_lines[0][1])
    region_lat_rad = math.radians(region_lat)       # rad
    region_long_rad = math.radians(region_long)     # rad
    gd = observation_class.Observation(region_lat_rad, region_long_rad)

    return gd

def get_gs():
    gs_lines = []
    input_f2 = open('settings/SELECT_GROUND_STATION.txt', 'r')
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
        gs_ele = float(gs_lines[g][2])
        # gs_ele = 10
        gs_lat_rad = math.radians(gs_lat)  # rad
        gs_long_rad = math.radians(gs_long)  # rad
        gs_ele_rad = math.radians(gs_ele)  # rad
        gs = GroundStation_class.GroundStation(gs_lat_rad, gs_long_rad, gs_ele_rad)
        gs_list.append(gs)

    return gs_list