import os
import xlwt
import time
# import numpy as np
import math
# import backup.include.imaging as imaging
import include.communication as communication
import include.greenwich as greenwich
import include.satclass as satclass
# import backup.include.gdclass as gdclass
import include.gsclass as gsclass
import include.satcompute as satcompute

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
start_greenwich = (greenwich.greenwich(start_time_julian)) % 360   # 0 to 360 degree

# ---------read ground stations
gs_lines = []
input_f2 = open('settings/SELECT_GROUND_STATION2.txt', 'r')
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
    gs = gsclass.GS(gs_lat_rad, gs_long_rad, gs_ele_rad)
    gs_list.append(gs)

# ----------main section
off_nadir = math.radians(45)
i_o = math.radians(97)
e_o = 0
omega_o = 0
circle_o = 14
m = 9                  # number of orbit
n = 25                 # number of sat

# remove existed output file
if os.path.exists("results/satellite_to_ground_communicable_result.xls"):
    os.remove("results/satellite_to_ground_communicable_result.xls")
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('sat_ground_communicable_result', cell_overwrite_ok=True)
col = ('Geocentric Latitude', 'Geocentric Longitude', 'Radius of Orbit', 'communicable')
for i in range(0, 4):
    sheet.write(0, i, col[i])
col_num = 1

# init satellite
sat_list = []
first_Omega = 0  # longitude of ascending node of the first orbit
even_Omega = 180 / (m-1)
for orbit_id in range(m):
    Omega_o = math.radians(first_Omega + orbit_id * even_Omega)
    first_M = 0  # first satellite postion of this orbit
    even_M = 360 / n
    for sat_id in range(n):
        M_o = math.radians(first_M + sat_id * even_M)
        # set current time to start time
        s = satclass.Sat(start_time_julian, i_o, Omega_o, e_o, omega_o, M_o, circle_o, start_time_julian)
        
        sat_list = sat_list + [s]

# satellite to ground station visible
for gs in gs_list:
    sheet.write(col_num, 0, math.degrees(gs.lat_rad))
    sheet.write(col_num, 1, math.degrees(gs.long_rad))
    visited_sats = []
    gs_off_nadir = math.asin(satclass.Re * math.cos(gs.ele_rad) / s.r)
    # search for all sat
    for s in sat_list:
        if communication.is_gs_communicable(0, s, gs, gs_off_nadir, start_greenwich):
            visited_sats.append(s)

    if visited_sats:
        for s in visited_sats:
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
book.save('results/satellite_to_ground_communicable_result.xls')