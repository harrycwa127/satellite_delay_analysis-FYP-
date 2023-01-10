import os
import xlwt
import time
import math
from include import Satellite_class
from include import GroundStation_class
from include import satcompute
from include import visibility
from include import read_data

start_time = time.time()

# ---------read start time and end time
start_time_julian, start_greenwich = read_data.get_start_julian_time()

# ---------read ground stations
gs_list = read_data.get_gs()


# remove existed output file
if os.path.exists("results/sat_to_sat_communicable_result.xls"):
    os.remove("results/sat_to_sat_communicable_result.xls")
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('sat_ground_communicable_result', cell_overwrite_ok=True)
col = ('Geocentric Latitude', 'Geocentric Longitude', 'Radius of Orbit', 'communicable')
for i in range(0, 4):
    sheet.write(0, i, col[i])
col_num = 1

# init satellite
off_nadir = math.radians(45)
i_o = math.radians(97)
e_o = 0
omega_o = 0
circle_o = 14
m = 9                  # number of orbit
n = 25                 # number of sat


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
        s = Satellite_class.Satellite(start_time_julian, i_o, Omega_o, e_o, omega_o, M_o, circle_o, start_time_julian)
        
        sat_list = sat_list + [s]

# satellite to ground station visible
for gs in gs_list:
    sheet.write(col_num, 0, math.degrees(gs.lat_rad))
    sheet.write(col_num, 1, math.degrees(gs.long_rad))
    visited_sats = []
    gs_off_nadir = math.asin(Satellite_class.Re * math.cos(gs.ele_rad) / s.r)
    # search for all sat
    for s in sat_list:
        if visibility.is_gs_communicable(0, s, gs, gs_off_nadir, start_greenwich):
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
book.save('results/sat_to_sat_communicable_result.xls')