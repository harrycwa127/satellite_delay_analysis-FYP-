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
from include.SimParameter_class import SimParameter

start_time = time.time()

# ---------read start time
start_time_julian, start_greenwich = read_data.get_start_julian_time()
SimParameter.set_start_greenwich(start_greenwich)

# obervation lat lon
gd = read_data.get_observation2()

# ---------read ground stations
gs_list = read_data.get_gs()


# init satellite
SimParameter.set_off_nadir(math.radians(45))
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
SimParameter.set_buffer_delay(0.05)        # (sec, e.g. 0.05, 50 ms)
SimParameter.set_process_delay(0.01)        # (sec, e.g. 0.01, 10 ms)
SimParameter.set_package_size(56623104)    # (Bytes) 54 Mb, 
SimParameter.set_data_rate(530579456)       # (Bytes/s) 506 Mb/s
SimParameter.set_signal_speed(299792458)

# time var
t = 0       # for store the current time passed from start time
temp = 0    # for get the result of communication

# remove orginal output file
if os.path.exists("results/analysis_result.xls"):
    os.remove("results/analysis_result.xls")
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('analysis_result', cell_overwrite_ok=True)
col = ('Satellite Latitude', 'Satellite Longitude', 'Satellite Altitude', 'Delay Time' )
for i in range(0, 4):
    sheet.write(0, i, col[i])
col_num = 1


# search satellite to observation
imaging_sat = -1
# search for all sat
for s in range(len(sat_list)):
    if visibility.is_observation_visible(0, sat_list[s], gd):
        imaging_sat = s
        break

# if no any satellite obervate the obervation point, exit
if imaging_sat == -1:
    print("No Satellite able to visit the observation point!!")
    sys.exit(-1)

# if the satellite obervate the the obervation point and able to directly commincation to the gs
gs = gs_list[0]         # target ground_station

# array to store the path result
sat_commnicate_path = []
sat_commnicate_delay = []

sat_commnicate_path, sat_commnicate_delay = communication.path_decision(sat_list, gd, gs)


for i in range(len(sat_commnicate_path)):
    if sat_commnicate_path[i] == -1:
        sheet.write(col_num, 0, -1)
        sheet.write(col_num, 1, -1)
        sheet.write(col_num, 2, -1)
        sheet.write(col_num, 3, sat_commnicate_delay[i])

        col_num += 1

    else:
        phi, lam = satcompute.get_sat_lat_lon(sat = sat_list[sat_commnicate_path[i]], t = sat_commnicate_delay[i])
        phi = phi * (180/math.pi)
        lam = lam * (180/math.pi)
        
        sheet.write(col_num, 0, phi)
        sheet.write(col_num, 1, lam)
        sheet.write(col_num, 2, sat_list[sat_commnicate_path[i]].r)
        sheet.write(col_num, 3, sat_commnicate_delay[i])

        col_num += 1


print("total delay of the commnication is", sat_commnicate_delay[len(sat_commnicate_delay)-1], "seconds.")


end_time = time.time()
print('overall time:',  end_time-start_time)
book.save('results/analysis_result.xls')