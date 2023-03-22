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

start_time = time.time()

# ---------read start time
start_time_julian, start_greenwich = read_data.get_start_julian_time()
Setting.start_greenwich = start_greenwich

# obervation lat lon
gd = read_data.get_observation2()

# ---------read ground stations
gs = read_data.get_gs()

# init satellite
Setting.off_nadir = math.radians(45)
i_o = math.radians(97)
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
        s = Satellite_class.Satellite(start_time_julian, i_o, Omega_o, omega_o, M_o, circle_o, start_time_julian)
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

# write the data the obervation and ground station
sheet.write(0, 1, "Latitude")
sheet.write(0, 2, "Longitude")

sheet.write(1, 0, "Observation Point")
sheet.write(1, 1, math.degrees(gd.lat_rad))
sheet.write(1, 2, math.degrees(gd.lon_rad))

sheet.write(2, 0, "Ground Station")
sheet.write(2, 1, math.degrees(gs.lat_rad))
sheet.write(2, 2, math.degrees(gs.lon_rad))

col = ('Satellite Latitude', 'Satellite Longitude', 'Satellite Altitude', 'Delay Time' )
for i in range(0, 4):
    sheet.write(4, i, col[i])
col_num = 5

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

time_delay = 0       # in sec

# time window of gd
time_delay = satcompute.sat_original_delay(gd, sat_list[imaging_sat], gs)
if time_delay < 0:
    print("not able to send data to the ground station!")
    sheet.write(col_num, 0, -1)
    sheet.write(col_num, 1, -1)
    sheet.write(col_num, 2, -1)
    sheet.write(col_num, 3, "NA")

# write result to excel
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

phi, lam = satcompute.get_sat_lat_lon(sat = sat_list[imaging_sat], t = time_delay)
phi = phi * (180/math.pi)
lam = lam * (180/math.pi)

if phi < 0:
    phi += 360

if lam < 0:
    lam += 360

sheet.write(col_num, 0, phi)
sheet.write(col_num, 1, lam)
sheet.write(col_num, 2, sat_list[imaging_sat].r)
sheet.write(col_num, 3, time_delay)

col_num += 1

print("total delay of the commnication is", time_delay, "seconds.")

end_time = time.time()
print('overall time:',  end_time-start_time)
book.save('results/orginal_delay_result.xls')