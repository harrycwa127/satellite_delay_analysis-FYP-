import os
import xlwt
import time
import math
from include import Satellite_class
from include import satcompute
from include import visibility
from include import read_data
from include.SimParameter_class import SimParameter


start_time = time.time()

# ---------read start time
start_time_julian, start_greenwich = read_data.get_start_julian_time()
SimParameter.set_start_greenwich(start_greenwich)


# obervation lat lon
gd_list = read_data.get_observation()

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
for i in range(len(gd_list)):
    sheet.write(col_num, 0, math.degrees(gd_list[i].lat_rad))
    sheet.write(col_num, 1, math.degrees(gd_list[i].lon_rad))
    imaging_sats = []
    for s in sat_list:
        if visibility.is_observation_visible(0, s, gd_list[i],):
            imaging_sats.append(s)

    temp = ''
    if imaging_sats:
        for s in imaging_sats:
            phi, lam = satcompute.get_sat_lat_lon(sat = s, t = 0)
            phi = phi * (180/math.pi)
            lam = lam * (180/math.pi)
            
            if temp == '':
                temp = "[%f, %f, %f]" % (phi, lam, s.r)
            else:
                temp += ", [%f, %f, %f]" % (phi, lam, s.r)

            sheet.write(col_num, 2, temp)
    else:
        sheet.write(col_num, 2, '-')
                

    col_num += 1
    
end_time = time.time()
print('overall time:',  end_time-start_time)
book.save('results/sat_to_gd_communicable_result.xls')


