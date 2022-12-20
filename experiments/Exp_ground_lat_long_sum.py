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
if os.path.exists("../results/ground_lat_long_sum.xls"):
    os.remove("../results/ground_lat_long_sum.xls")
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('ground_lat_long_sum', cell_overwrite_ok=True)
col = ('ground latitude', 'min visits', 'max visits', 'average visits', 'min duration', 'max duration', 'average duration')
for i in range(0, 7):
    sheet.write(0, i, col[i])

s = Sat(start_time_julian, i_o, Omega_o, e_o, omega_o, M_o, circle_o, start_time_julian)
col_num = 1
for ground_lat in ground_lat_list:
    min_visit = 100
    max_visit = 0
    average_visit = 0
    min_duration = 10000
    max_duration = 0
    average_duration = 0
    sum_visit = 0
    sum_duration = 0
    for ground_long in ground_long_list:
        gd = GD(math.radians(ground_lat), math.radians(ground_long))
        imaging_curve = imaging.visible(time_interval, start_greenwich, s, gd, math.radians(off_nadir))
        visit = len(imaging_curve)
        if visit > max_visit:
            max_visit = visit
        if visit < min_visit:
            min_visit = visit
        sum_visit = sum_visit+visit
        for i in range(visit):
            min_i = imaging_curve[i][0]
            max_i = imaging_curve[i][1]
            duration = round(max_i - min_i, 1)
            if duration > max_duration:
                max_duration = duration
            if duration < min_duration:
                min_duration = duration
            sum_duration = sum_duration + duration
    average_visit = sum_visit/len(ground_long_list)
    average_duration = sum_duration/sum_visit
    sheet.write(col_num, 0, str(ground_lat))
    sheet.write(col_num, 1, str(min_visit))
    sheet.write(col_num, 2, str(max_visit))
    sheet.write(col_num, 3, str(average_visit))
    sheet.write(col_num, 4, str(min_duration))
    sheet.write(col_num, 5, str(max_duration))
    sheet.write(col_num, 6, str(average_duration))
    col_num = col_num + 1
book.save('../results/ground_lat_long_sum.xls')

