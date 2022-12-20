import math
import os
import xlwt
from include import imaging
from include import curve
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

off_nadir = math.radians(45)
region_lat_rad = math.radians(48)      # 弧度
region_long_rad = math.radians(9)     # 弧度
gd = GD(region_lat_rad, region_long_rad)

# ----------main section
i_o = math.radians(50)
e_o = 0
omega_o = 0
circle_o = 14
m_set = [5]
n_set = [10, 20, 25, 30, 35, 40, 50, 60]

request_period_list = [600]    # request period (s)
request_postpone_list = [60]     # request postpone (s)

# 删除output文件
if os.path.exists("../results/satellite_constellation.xls"):
    os.remove("../results/satellite_constellation.xls")
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('satellite_constellation', cell_overwrite_ok=True)
col = ('orbit number', 'satellites per orbit', 'request period', 'valid', 'satisfied request number')
for i in range(0, 5):
    sheet.write(0, i, col[i])

col_num = 1
for m in m_set:
    for n in n_set:
        sheet.write(col_num, 0, str(m))
        sheet.write(col_num, 1, str(n))
        imaging_curve = []
        # ------初始化所有卫星
        sat_list = []
        first_Omega = 0  # 第一个轨道的升交点赤经
        even_Omega = 180 / (m-1)
        for orbit_id in range(m):
            Omega_o = math.radians(first_Omega + orbit_id * even_Omega)
            first_M = 0  # 轨道上的第一个卫星的位置
            even_M = 360 / n
            for sat_id in range(n):
                M_o = math.radians(first_M + sat_id * even_M)
                # 令卫星的当前时间为simulation的开始时间
                s = Sat(start_time_julian, i_o, Omega_o, e_o, omega_o, M_o, circle_o, start_time_julian)
                sat_list = sat_list + [s]
        # 对每个卫星求其观测curve，然后merge成星座的观测curve
        for sid in range(m*n):
            sid_imaging_curve = imaging.visible(time_interval, start_greenwich, sat_list[sid], gd, off_nadir)
            imaging_curve = curve.merge_curve(imaging_curve, sid_imaging_curve)
        # validation
        for i in range(len(request_period_list)):
            request_period = request_period_list[i]
            request_postpone = request_postpone_list[i]
            sheet.write(col_num, 2, str(request_period))
            request_num = int(time_interval / request_period)
            request = [[0+request_period*x, request_postpone+request_period*x] for x in range(request_num)]
            rid_list = curve.get_responding_rid(imaging_curve, request, request_period, request_postpone)
            rid_set = []   # 最终满足的所有request
            for j in range(len(rid_list)):
                rid_set = rid_set + rid_list[j]
            rid_set = list(set(rid_set))
            rid_set_len = len(rid_set)
            if rid_set_len >= request_num:
                sheet.write(col_num, 3, 'V')
                print('valid')
            else:
                print('invalid')
                sheet.write(col_num, 3, '-')
                sheet.write(col_num, 4, str(rid_set_len))
            col_num = col_num + 1
print('finish')
book.save('../results/satellite_constellation.xls')






