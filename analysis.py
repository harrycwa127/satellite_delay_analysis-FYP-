import os
import xlwt
import time
import math
import sys
from include import Satellite_class
from include import communication
from include import visibility
from include import read_data
from include import satcompute

start_time = time.time()

# ---------read start time
start_time_julian, start_greenwich = read_data.get_start_julian_time()

# obervation lat lon
gd = read_data.get_observation2()

# ---------read ground stations
gs_list = read_data.get_gs()


# init satellite
off_nadir = math.radians(45)
i_o = math.radians(97)
e_o = 0
omega_o = 0
circle_o = 14
m = 9
n = 25

sat_list = []
first_Omega = 0  # first right ascension of ascending node (rad)
even_Omega = 180 / (m-1)
for orbit_id in range(m):
    Omega_o = math.radians(first_Omega + orbit_id * even_Omega)
    first_M = 0  # first satellite posistion in the orbit
    even_M = 360 / n
    for sat_id in range(n):
        M_o = math.radians(first_M + sat_id * even_M)
        # set time to the start time
        s = Satellite_class.Satellite(start_time_julian, i_o, Omega_o, e_o, omega_o, M_o, circle_o, start_time_julian)
        sat_list = sat_list + [s]


# data commnication delay init
buffer_delay  = 0.05        # (sec, e.g. 0.05, 50 ms)
process_delay = 0.01        # (sec, e.g. 0.01, 10 ms)
package_size = 56623104    # (Bytes) 54 Mb, 
data_rate = 530579456       # (Bytes/s) 506 Mb/s

# time var
t = 0       # for store the current time passed from start time
temp = 0    # for get the result of communication

# remove orginal output file
if os.path.exists("results/analysis_result.xls"):
    os.remove("results/analysis_result.xls")
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('analysis_result', cell_overwrite_ok=True)
col = ('Obervation Latitude', 'Obervation Longitude', 'Visited Satellite')
for i in range(0, 3):
    sheet.write(0, i, col[i])
col_num = 1


# search satellite to observation
imaging_sat = -1
# search for all sat
for s in range(len(sat_list)):
    if visibility.is_observation_visible(0, sat_list[s], gd, off_nadir, start_greenwich):
        imaging_sat = s
        break

# if no any satellite obervate the obervation point, exit
if imaging_sat == -1:
    print("No Satellite able to visit the observation point!!")
    sys.exit(-1)

# if the satellite obervate the the obervation point and able to directly commincation to the gs
gs = gs_list[0]         # target ground_station
# search for all sat
for s in sat_list:
    gs_off_nadir = math.asin(Satellite_class.Re * math.cos(gs.ele_rad) / s.r)
    if visibility.is_gs_communicable(0, s, gs, gs_off_nadir, start_greenwich):
        temp = communication.sat_ground_commnicate(0, package_size, data_rate, imaging_sat, gs, buffer_delay, process_delay, gs_off_nadir, start_greenwich)
        if temp > 0:
            print("Satellite direcly get obervation point and ground station!")
            print("Commnication Delay is:" + temp)
            sys.exit(0)


# no able to directly transfer data from obervation satellite to ground station
sat_commnicate_path = []
sat_commnicate_path.append(imaging_sat)
sat_num = 0         #index of the last element in sat_commnicate_path
while visibility.is_gs_communicable(t, sat_commnicate_path[sat_num], gs, gs_off_nadir, start_greenwich) == True:
    ignore_sat = []
    ignore = True
    while ignore == True:
        min_distance = -1        # store the min distance from next satellite to gs
        min_sat = -1            # store the min distance satellite object
        distance = 0

        for s in range(len(sat_list)):      # avoid the sat not able to communicate
            if s not in ignore_sat and s not in sat_commnicate_path:
                if visibility.is_sat_communicable(t, sat_commnicate_path[sat_num], sat_list[s]):
                    distance = satcompute.sat_ground_distance(t, sat_list[s], gs)
                    if min_distance == -1:
                        min_distance = distance
                        min_sat = s
                    elif distance < min_distance:
                        min_distance = distance
                        min_sat = s

        # has sat in vibility
        if min_sat != -1:
            temp = communication.inter_sat_commnicate(t, package_size, data_rate, sat_commnicate_path[sat_num], sat_list[min_sat], buffer_delay, process_delay)
            if temp > 0:
                # commnicate success
                t = temp
                sat_commnicate_path.append(sat_list[min_sat])
                sat_num += 1
                ignore = False

            else:
                # commnication fail, loop again and ignore that sat
                ignore = True
                ignore_sat.append(min_sat)
        # wait 1 sec and check visibility again
        else:
            t += 1

end_time = time.time()
print('overall time:',  end_time-start_time)
book.save('results/analysis_result.xls')


