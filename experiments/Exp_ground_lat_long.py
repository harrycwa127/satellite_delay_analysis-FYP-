import os
import xlwt
from include import imaging
from include.greenwich import *
from include.satclass import *
from include.gdclass import *


# ---------read start time and end time
time_f = open('../settings/TIME_INTERVAL.txt', 'r')
time_lines = []
for line in time_f.readlines():
    time_lines.append(line.split())
start_time_julian = julian2(int(time_lines[0][0]), int(time_lines[0][1]), int(time_lines[0][2]),
                                      int(time_lines[0][3]), int(time_lines[0][4]), int(time_lines[0][5]))
end_time_julian = julian2(int(time_lines[1][0]), int(time_lines[1][1]), int(time_lines[1][2]),
                                    int(time_lines[1][3]), int(time_lines[1][4]), int(time_lines[1][5]))
time_interval = (end_time_julian-start_time_julian)*86400  # 单位s
start_greenwich = (greenwich(start_time_julian)) % 360   # 转到0到360°

# ---------basic settings
i_o = math.radians(97)
Omega_o = 0
e_o = 0
omega_o = 0
M_o = 0
circle_o = 14
off_nadir = 45
T = 86400/circle_o
ground_lat_list = [80, 45, 10]
ground_long_list = [10*x for x in range(36)]

# 删除output文件
if os.path.exists("../results/ground_lat_long.xls"):
    os.remove("../results/ground_lat_long.xls")
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('ground_lat_long', cell_overwrite_ok=True)
col = ('ground latitude', 'ground longitude', 'circle number', 'duration')
for i in range(0, 4):
    sheet.write(0, i, col[i])

s = Sat(start_time_julian, i_o, Omega_o, e_o, omega_o, M_o, circle_o, start_time_julian)
col_num = 1
for ground_lat in ground_lat_list:
    for ground_long in ground_long_list:
        gd = GD(math.radians(ground_lat), math.radians(ground_long))
        circle_num_list = []
        duration_list = []
        imaging_curve = imaging.visible(time_interval, start_greenwich, s, gd, math.radians(off_nadir))
        for i in range(len(imaging_curve)):
            min_i = imaging_curve[i][0]
            max_i = imaging_curve[i][1]
            circle_num_list.append(int(min_i / T))
            duration = round(max_i - min_i, 1)
            duration_list.append(duration)
        sheet.write(col_num, 0, str(ground_lat))
        sheet.write(col_num, 1, str(ground_long))
        sheet.write(col_num, 2, str(circle_num_list))
        sheet.write(col_num, 3, str(duration_list))
        col_num = col_num + 1
book.save('../results/ground_lat_long.xls')

