import os
import xlwt
import time
import math
from include import greenwich
from include import Satellite_class
from include import observation_class
from include import satcompute
from include import visibility

start_time = time.time()

# ---------read start time and end time
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

# obervation lat lon
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

# ----------main section
off_nadir = math.radians(45)
i_o = math.radians(97)
e_o = 0
omega_o = 0
circle_o = 14
m = 9
n = 25

# init satellite
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

# remove orginal output file
if os.path.exists("results/sat_to_gd_communicable_result.xls"):
    os.remove("results/sat_to_gd_communicable_result.xls")
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('sat_to_gd_communicable_result', cell_overwrite_ok=True)
col = ('Obervation Latitude', 'Obervation Longitude', 'Visited Satellite')
for i in range(0, 3):
    sheet.write(0, i, col[i])
col_num = 1

# search
for i in range(gd_accounts):
    sheet.write(col_num, 0, math.degrees(gd_list[i].lat_rad))
    sheet.write(col_num, 1, math.degrees(gd_list[i].long_rad))
    imaging_sats = []
    for s in sat_list:
        if visibility.is_visible(0, s, gd_list[i], off_nadir, start_greenwich):
            imaging_sats.append(s)

    # 若没有卫星可看到地面点，则该次搜索失败，直接下次搜索
    if imaging_sats:
        for s in imaging_sats:
            phi, lam = satcompute.get_sat_geo_lat_lon(sat = s, t = 0, start_greenwich = start_greenwich)
            phi = phi * (180/math.pi)
            lam = lam * (180/math.pi)
            
            temp = "[%f, %f, %f]" % (phi, lam, s.r)

            sheet.write(col_num, 2, temp)
    else:
        sheet.write(col_num, 2, '-')
                

    col_num += 1
    
end_time = time.time()
print('overall time:',  end_time-start_time)
book.save('results/sat_to_gd_communicable_result.xls')


