import os
import xlwt
import time
import math
from include import Satellite_class
from include import communication
from include import read_data
from include import satcompute
from include.Display_class import Display
from include.Setting_class import Setting

start_time = time.time()

# ---------read start time
start_time_julian, start_greenwich = read_data.get_start_julian_time()
Setting.start_greenwich = start_greenwich

# obervation lat lon
gd = read_data.get_observation2()

# ---------read ground stations
gs = read_data.get_gs()

# call Setting UI
Setting.display()

# init parameter for simulator
# Setting.inclination = math.radians(97)
# Setting.argument_of_perigee = 0
# Setting.motion = 14   # mean motion (revolutions per day)
# Setting.orbit_size = 9  # define numbers of orbit
# Setting.sat_size = 25   # define numbers of satellite in each orbit

# data commnication delay init
# Setting.off_nadir = math.radians(45)
# Setting.buffer_delay = 0.05         # (sec, e.g. 0.05, 50 ms)
# Setting.process_delay = 0.01        # (sec, e.g. 0.01, 10 ms)
# Setting.package_size = 56623104     # (Bytes) 54 Mb, 
# Setting.data_rate = 530579456       # (Bytes/s) 506 Mb/s
# Setting.signal_speed = 299792458    # (m/s)

sat_list = []
first_Omega = 0  # first right ascension of ascending node (rad)
even_Omega = 180 / (Setting.orbit_size-1)
for orbit_id in range(Setting.orbit_size):
    Omega_o = math.radians(first_Omega + orbit_id * even_Omega)
    first_M = 0  # first satellite posistion in the orbit
    even_M = 360 / Setting.sat_size
    for sat_id in range(Setting.sat_size):
        M_o = math.radians(first_M + sat_id * even_M)
        # set time to the start time
        s = Satellite_class.Satellite(start_time_julian, Setting.inclination, Omega_o, Setting.argument_of_perigee, M_o, Setting.motion, start_time_julian)
        sat_list = sat_list + [s]


# remove orginal output file
if os.path.exists("results/analysis_result.xls"):
    os.remove("results/analysis_result.xls")
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('astar_analysis_result', cell_overwrite_ok=True)

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

# array to store the path result
astar_sat_commnicate_path, astar_sat_commnicate_delay = communication.astar_path_decision(sat_list, gd, gs)
dijkstra_sat_commnicate_path, dijkstra_sat_commnicate_delay = communication.dijkstra_path_decision(sat_list, gd, gs)
orbit_sat_commnicate_path, orbit_sat_commnicate_delay = communication.orbit_path_decision(sat_list, gd, gs, Setting.sat_size)

for i in range(len(astar_sat_commnicate_path)):
    if astar_sat_commnicate_path[i] == -1:
        sheet.write(col_num, 0, -1)
        sheet.write(col_num, 1, -1)
        sheet.write(col_num, 2, -1)
        sheet.write(col_num, 3, astar_sat_commnicate_delay[i])

        col_num += 1

    elif astar_sat_commnicate_path[i] == "gs":
        sheet.write(col_num, 0, "Ground Station")
        sheet.write(col_num, 1, "Ground Station")
        sheet.write(col_num, 2, 0)
        sheet.write(col_num, 3, astar_sat_commnicate_delay[i])

    else:
        phi, lam = satcompute.get_sat_lat_lon(sat = sat_list[astar_sat_commnicate_path[i]], t = astar_sat_commnicate_delay[i])
        phi = phi * (180/math.pi)
        lam = lam * (180/math.pi)

        if phi < 0:
            phi += 360

        if lam < 0:
            lam += 360
        
        sheet.write(col_num, 0, phi)
        sheet.write(col_num, 1, lam)
        sheet.write(col_num, 2, sat_list[astar_sat_commnicate_path[i]].r)
        sheet.write(col_num, 3, astar_sat_commnicate_delay[i])

        col_num += 1

print("Total delay of the A* Path is", astar_sat_commnicate_delay[-1], "seconds.")


sheet = book.add_sheet('dijkstra_analysis_result', cell_overwrite_ok=True)
# write the data the obervation and ground station
sheet.write(0, 1, "Latitude")
sheet.write(0, 2, "Longitude")

sheet.write(1, 0, "Observation Point")
sheet.write(1, 1, math.degrees(gd.lat_rad))
sheet.write(1, 2, math.degrees(gd.lon_rad))

sheet.write(2, 0, "Ground Station")
sheet.write(2, 1, math.degrees(gs.lat_rad))
sheet.write(2, 2, math.degrees(gs.lon_rad))

col = ('Satellite Latitude', 'Satellite Longitude', 'Satellite Altitude', 'Delay Time')
for i in range(0, 4):
    sheet.write(4, i, col[i])
col_num = 5

for i in range(len(dijkstra_sat_commnicate_path)):
    if dijkstra_sat_commnicate_path[i] == -1:
        sheet.write(col_num, 0, -1)
        sheet.write(col_num, 1, -1)
        sheet.write(col_num, 2, -1)
        sheet.write(col_num, 3, dijkstra_sat_commnicate_delay[i])

        col_num += 1

    elif dijkstra_sat_commnicate_path[i] == "gs":
        sheet.write(col_num, 0, "Ground Station")
        sheet.write(col_num, 1, "Ground Station")
        sheet.write(col_num, 2, 0)
        sheet.write(col_num, 3, dijkstra_sat_commnicate_delay[i])

    else:
        phi, lam = satcompute.get_sat_lat_lon(sat = sat_list[dijkstra_sat_commnicate_path[i]], t = dijkstra_sat_commnicate_delay[i])
        phi = phi * (180/math.pi)
        lam = lam * (180/math.pi)

        if phi < 0:
            phi += 360

        if lam < 0:
            lam += 360
        
        sheet.write(col_num, 0, phi)
        sheet.write(col_num, 1, lam)
        sheet.write(col_num, 2, sat_list[dijkstra_sat_commnicate_path[i]].r)
        sheet.write(col_num, 3, dijkstra_sat_commnicate_delay[i])

        col_num += 1

print("Total delay of the Dijkstra Path is", dijkstra_sat_commnicate_delay[-1], "seconds.")

sheet = book.add_sheet('orbit_analysis_result', cell_overwrite_ok=True)
# write the data the obervation and ground station
sheet.write(0, 1, "Latitude")
sheet.write(0, 2, "Longitude")

sheet.write(1, 0, "Observation Point")
sheet.write(1, 1, math.degrees(gd.lat_rad))
sheet.write(1, 2, math.degrees(gd.lon_rad))

sheet.write(2, 0, "Ground Station")
sheet.write(2, 1, math.degrees(gs.lat_rad))
sheet.write(2, 2, math.degrees(gs.lon_rad))

col = ('Satellite Latitude', 'Satellite Longitude', 'Satellite Altitude', 'Delay Time')
for i in range(0, 4):
    sheet.write(4, i, col[i])
col_num = 5

for i in range(len(orbit_sat_commnicate_path)):
    if orbit_sat_commnicate_path[i] == -1:
        sheet.write(col_num, 0, -1)
        sheet.write(col_num, 1, -1)
        sheet.write(col_num, 2, -1)
        sheet.write(col_num, 3, orbit_sat_commnicate_delay[i])

        col_num += 1

    elif orbit_sat_commnicate_path[i] == "gs":
        sheet.write(col_num, 0, "Ground Station")
        sheet.write(col_num, 1, "Ground Station")
        sheet.write(col_num, 2, 0)
        sheet.write(col_num, 3, orbit_sat_commnicate_delay[i])

    else:
        phi, lam = satcompute.get_sat_lat_lon(sat = sat_list[orbit_sat_commnicate_path[i]], t = orbit_sat_commnicate_delay[i])
        phi = phi * (180/math.pi)
        lam = lam * (180/math.pi)

        if phi < 0:
            phi += 360

        if lam < 0:
            lam += 360
        
        sheet.write(col_num, 0, phi)
        sheet.write(col_num, 1, lam)
        sheet.write(col_num, 2, sat_list[orbit_sat_commnicate_path[i]].r)
        sheet.write(col_num, 3, orbit_sat_commnicate_delay[i])

        col_num += 1

print("Total delay of the Orbit-Base Path is", orbit_sat_commnicate_delay[-1], "seconds.")


end_time = time.time()
print('overall time:',  end_time-start_time)
book.save('results/analysis_result.xls')

Display.set_point_info(gd, sat_list, astar_sat_commnicate_path, astar_sat_commnicate_delay,\
                        orbit_sat_commnicate_path, orbit_sat_commnicate_delay,\
                        dijkstra_sat_commnicate_path, dijkstra_sat_commnicate_delay, gs)
Display.display()