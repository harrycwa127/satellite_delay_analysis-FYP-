import random
import os
import xlwt
import time
import numpy as np
from backup.imaging import *
from include.communication import *
from include.greenwich import *
from include.Satellite_class import *
from include.observation_class import *
from include.GroundStation_class import *

start_time = time.time()
requestNum = 144

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

# ----------观测区域经纬度
gd_lines = []
obs_f = open('../settings/OBSERVATION.txt', 'r')
for line in obs_f.readlines():
    gd_lines.append(line.split(' '))
obs_f.close()
gd_accounts = len(gd_lines)
gd_list = []
for g in range(gd_accounts):
    region_lat = float(gd_lines[g][0])
    region_long = float(gd_lines[g][1])
    region_lat_rad = math.radians(region_lat)       # 弧度
    region_long_rad = math.radians(region_long)     # 弧度
    gd = Observation(region_lat_rad, region_long_rad)
    gd_list.append(gd)

# ---------read ground stations
gs_lines = []
input_f2 = open('../settings/SELECT_GROUND_STATION2.txt', 'r')
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
    gs_lat_rad = math.radians(gs_lat)  # 弧度
    gs_long_rad = math.radians(gs_long)  # 弧度
    gs_ele_rad = math.radians(gs_ele)  # 弧度
    gs = GroundStation(gs_lat_rad, gs_long_rad, gs_ele_rad)
    gs_list.append(gs)

# ----------main section
off_nadir = math.radians(45)
i_o = math.radians(97)
e_o = 0
omega_o = 0
circle_o = 14
m = 9
n = 25

request_period = 600   # request period (s)
request_postpone = 60  # request postpone (s)

img_cost = 1           # imaging cost (s)
com_cost = 15          # communication cost (s)
ser_ddl = 150          # service delay (s)

# 删除output文件
if os.path.exists("results/baseline_result.xls"):
    os.remove("results/baseline_result.xls")
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('baseline_result', cell_overwrite_ok=True)
col = ('ground latitude', 'ground longitude', 'feasible')
for i in range(0, 3):
    sheet.write(0, i, col[i])
col_num = 1

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
        s = Satellite(start_time_julian, i_o, Omega_o, e_o, omega_o, M_o, circle_o, start_time_julian)
        sat_list = sat_list + [s]

# ------穷举搜索
for i in range(gd_accounts):
    sheet.write(col_num, 0, math.degrees(gd_list[i].lat_rad))
    sheet.write(col_num, 1, math.degrees(gd_list[i].long_rad))
    valid = 0
    for offset_start in np.arange(0, 600, 0.1):
        result_lst = [0]*requestNum
        result = 0
        for reqNum in range(requestNum):  # check 144个t
            t_start = offset_start+request_period*reqNum
            # 由于request有postpone=60s，因此需要遍历，step=0.1s
            for t in np.arange(t_start, t_start+request_postpone, 0.1):
                imaging_sats = []      # 所有可在[t,t+1]观测到地面点的卫星集合
                for s in sat_list:
                    if is_observation_visible(t, s, gd_list[i], off_nadir, start_greenwich) and is_observation_visible(t+1, s, gd_list[i]
                            , off_nadir, start_greenwich):
                        imaging_sats = imaging_sats+[s]
                # 若没有卫星可看到地面点，则该次搜索失败，直接下次搜索
                if not imaging_sats:
                    print('can not image the ground')
                    continue
                #print('can image the ground')
                # 看能否通信
                communicate_flag = 0
                for s in imaging_sats:
                    for g in range(gs_accounts):
                        gs = gs_list[g]
                        gs_off_nadir = math.asin(Satellite_class.Re * math.cos(gs.ele_rad) / s.r)
                        communicate_dur = 0  # 将通信时段初始值设为0
                        flag = 0
                        for ct in np.arange(t, t+151, 0.1):
                            if is_gs_communicable(ct, s, gs, gs_off_nadir, start_greenwich):
                                communicate_dur = communicate_dur+1
                            else:
                                communicate_dur = 0
                            if communicate_dur >= 150:
                                communicate_flag = 1
                                break
                        if communicate_flag == 1:
                            break
                    if communicate_flag == 1:
                        break
                if communicate_flag == 1:
                    result_lst[reqNum] = 1
                    result = result+1
                    break
            if result_lst[reqNum] == 0:
                print("offset fail!!")
                break
        print("result list:", result_lst)
        if result == requestNum:
            valid = 1
            break
    if valid:
        sheet.write(col_num, 2, 'V')
        print('valid')
    else:
        sheet.write(col_num, 2, '-')
        print('invalid')
    col_num = col_num+1
end_time = time.time()
print('overall time:',  end_time-start_time)
book.save('results/baseline_result.xls')


