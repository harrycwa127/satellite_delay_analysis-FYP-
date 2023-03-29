import os
import xlwt
import time
import math
from include import Satellite_class
from include import satcompute
from include import visibility
from include import read_data
from include.Setting_class import Setting



start_time = time.time()

# ---------read start time and end time


# ---------read ground stations
gs_list = read_data.get_select_gs()


# remove existed output file
if os.path.exists("results/sat_to_gs_distance_result.xls"):
    os.remove("results/sat_to_gs_distance_result.xls")
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('sat_ground_communicable_result', cell_overwrite_ok=True)
col = ('Latitude', 'Longitude', 'Height', 'distance')
for i in range(0, 4):
    sheet.write(0, i, col[i])
col_num = 1

# init satellite
off_nadir = math.radians(45)
i_o = math.radians(97)
omega_o = 0
circle_o = 14
m = 9                  # number of orbit
n = 25                 # number of sat

t = 0


sat_list = []
first_Omega = 0  # longitude of ascending node of the first orbit
even_Omega = 180 / m
for orbit_id in range(m):
    Omega_o = math.radians(first_Omega + orbit_id * even_Omega)
    first_M = 0  # first satellite posGGtion of this orbit
    even_M = 360 / n
    for sat_id in range(n):
        M_o = math.radians(first_M + sat_id * even_M)
        # set current time to start time
        s = Satellite_class.Satellite(Setting.start_time_julian, i_o, Omega_o, omega_o, M_o, circle_o, Setting.start_time_julian)
        
        sat_list = sat_list + [s]

# satellite to ground station visible
for gs in gs_list:
    sheet.write(col_num, 0, math.degrees(gs.lat_rad))
    sheet.write(col_num, 1, math.degrees(gs.lon_rad))
    visited_sats = []
    # search for all sat
    for s in sat_list:
        gs_off_nadir = math.asin(Satellite_class.Re * math.cos(gs.ele_rad) / s.r)
        
        if visibility.is_gs_communicable(t, s, gs):
            visited_sats.append(s)

    if visited_sats:
        for s in visited_sats:
            phi, lam = satcompute.get_sat_lat_lon(sat = s, t = 0)
            phi = phi * (180/math.pi)
            lam = lam * (180/math.pi)
            distance = satcompute.sat_ground_distance(t, s, gs)
            
            sheet.write(col_num, 0, phi)
            sheet.write(col_num, 1, lam)
            sheet.write(col_num, 2, s.r)
            sheet.write(col_num, 3, distance)


    else:
        sheet.write(col_num, 2, '-')
                

    col_num += 1

end_time = time.time()
print('overall time:',  end_time-start_time)
book.save('results/sat_to_gs_distance_result.xls')