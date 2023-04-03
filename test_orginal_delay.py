import os
import xlwt
import time
import math
import sys
from include import Satellite_class
from include import visibility
from include import read_data
from include import satcompute
from include.Setting_class import Setting
from include import communication

start_time = time.time()

# ---------read start time


# obervation lat lon
gd = read_data.get_observation2()

# ---------read ground stations
gs = read_data.get_select_gs()

# init satellite
Setting.off_nadir = math.radians(45)
i_o = math.radians(97)
omega_o = 0
circle_o = 14
m = 9
n = 25

sat_list = []
first_Omega = 0  # first right ascension of ascending node (rad)
even_Omega = 180 / m
for orbit_id in range(m):
    Omega_o = math.radians(first_Omega + orbit_id * even_Omega)
    first_M = 0  # first satellite posistion in the orbit
    even_M = 360 / n
    for sat_id in range(n):
        M_o = math.radians(first_M + sat_id * even_M)
        # set time to the start time
        s = Satellite_class.Satellite(Omega_o, M_o, Setting.start_time_julian)
        sat_list = sat_list + [s]


# data commnication delay init
Setting.buffer_delay = 0.05        # (sec, e.g. 0.05, 50 ms)
Setting.process_delay = 0.01        # (sec, e.g. 0.01, 10 ms)
Setting.package_size = 56623104    # (Bytes) 54 Mb, 
Setting.data_rate = 530579456       # (Bytes/s) 506 Mb/s
Setting.signal_speed = 299792458    # speed of radio, near the speed of light

# remove orginal output file
if os.path.exists("results/orginal_method_result.xls"):
    os.remove("results/orginal_method_result.xls")
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('orginal_method_result', cell_overwrite_ok=True)

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

t = 0

reach = False
# find time can commnicate with, in sec
while reach == False:
    for gs_element in gs:
        if visibility.is_gs_communicable(t, sat_list[imaging_sat], gs_element):
            reach = True
            reached_gs = gs_element
            break
        else:
            t += 1
    

# rollback 1 sec and find time in 0.01
while reach == True and t >= 0:
    for gs_element in gs:
        if visibility.is_gs_communicable(t, sat_list[imaging_sat], gs_element):
            reach = False
            break
        else:
            t-=0.01

t += 0.01

communication_end = False
total_t = t
while communication_end == False:
    temp = communication.sat_ground_commnicate(t, sat_list[imaging_sat], reached_gs)
    if temp > 0:
        t = temp
        communication_end = True
    else:
        t -= 0.001

        if total_t - t > 1:
            print("Satellite Orginal Communication Fail!!")
            t = -1

# write result to excel
# write the data the obervation and ground station
sheet.write(0, 1, "Latitude")
sheet.write(0, 2, "Longitude")

sheet.write(1, 0, "Observation Point")
sheet.write(1, 1, math.degrees(gd.lat_rad))
sheet.write(1, 2, math.degrees(gd.lon_rad))

sheet.write(2, 0, "Ground Station")
sheet.write(2, 1, math.degrees(reached_gs.lat_rad))
sheet.write(2, 2, math.degrees(reached_gs.lon_rad))

col = ('Satellite Latitude', 'Satellite Longitude', 'Satellite Altitude', 'Delay Time' )
for i in range(0, 4):
    sheet.write(4, i, col[i])
col_num = 5

phi, lam = satcompute.get_sat_lat_lon(sat = sat_list[imaging_sat], t = 0)
phi = phi * (180/math.pi)
lam = lam * (180/math.pi)

if phi < 0:
    phi += 360

if lam < 0:
    lam += 360

sheet.write(col_num, 0, phi)
sheet.write(col_num, 1, lam)
sheet.write(col_num, 2, sat_list[imaging_sat].r)
sheet.write(col_num, 3, 0)

col_num += 1

phi, lam = satcompute.get_sat_lat_lon(sat = sat_list[imaging_sat], t = t)
phi = phi * (180/math.pi)
lam = lam * (180/math.pi)

if phi < 0:
    phi += 360

if lam < 0:
    lam += 360

sheet.write(col_num, 0, phi)
sheet.write(col_num, 1, lam)
sheet.write(col_num, 2, sat_list[imaging_sat].r)
sheet.write(col_num, 3, t)

col_num += 1

print("total delay of the commnication is", t, "seconds.")

end_time = time.time()
print('overall time:',  end_time-start_time)
book.save('results/orginal_delay_result.xls')