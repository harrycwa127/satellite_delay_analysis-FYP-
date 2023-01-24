import os
import xlwt
import time
import math
import sys
from include import Satellite_class
from include import communication
from include import visibility
from include import read_data

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
buffer_delay  = 0.06        # (sec, e.g. 0.06, 60 ms)
process_delay = 0           # (sec)
package_size = 54           # (Bytes) ?????
data_rate = 0               # (B/s)
signal_speed = 299792458    #  radio speed near speed of light, 299,792,458 m per second, value in signal_speed is m/s

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
imaging_sats = []
# search for all sat
for s in sat_list:
    if visibility.is_observation_visible(0, s, gd, off_nadir, start_greenwich):
        imaging_sats.append(s)

if not imaging_sats:
    print("No Satellite able to visit the observation point!!")
    sys.exit(-1)

visited_sats = []
for gs in gs_list:
    gs_off_nadir = math.asin(Satellite_class.Re * math.cos(gs.ele_rad) / s.r)
    # search for all sat
    for s in imaging_sats:
        if visibility.is_gs_communicable(0, s, gs, gs_off_nadir, start_greenwich):
            temp = communication.sat_ground_commnicate(0, package_size, data_rate, signal_speed, s, gs, buffer_delay, process_delay, package_size)
            if temp > 0:
                print("Satellite direcly get obervation point and ground station!")
                print("Commnication Delay is:" + temp)
                sys.exit(0)


# no able to directly transfer data from obervation satellite to ground station
for img_s in imaging_sats:
    for s in sat_list:
        if visibility.is_sat_communicable(t, img_s, s):
            temp = communication.inter_sat_commnicate(t, package_size, data_rate, signal_speed, img_s, s, buffer_delay, process_delay, package_size)
            if temp > 0:
                # commnicate success
                t = temp
            else:
                # commnicate fail
                pass

end_time = time.time()
print('overall time:',  end_time-start_time)
book.save('results/analysis_result.xls')


