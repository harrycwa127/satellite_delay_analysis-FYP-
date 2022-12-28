from include import satclass
from include import gsclass
from include import satcompute
import math


# 判断当前时刻卫星是否能和地面站通信
# 输入：1.当前时刻t（相对于开始时刻的时间）
#      2.卫星class
#      3.地面站class
#      4.由地面站通信的最小仰角得到的最大的off_nadir角
#      4.开始时刻0经度所处的赤经
# 输出：TRUE OR FALSE
def is_gs_communicable(t, satellite: satclass.Sat, gs: gsclass.GS, gs_off_nadir, start_greenwich):
    phi, lam = satcompute.get_sat_geo_lat_lon(sat = satellite, t = t, start_greenwich = start_greenwich)
    
    theta = lam - gs.long_rad
    cos_psi = math.cos(gs.lat_rad) * math.cos(phi) * math.cos(theta) + math.sin(gs.lat_rad) * math.sin(phi)
    psi = math.acos(cos_psi)
    beta = math.atan(satclass.Re * math.sin(psi) / (satellite.r - satclass.Re * math.cos(psi)))  # off nadir angle, 注意atan得到的是[-pi/2,pi/2]

    if cos_psi > (satclass.Re / satellite.r) and beta <= gs_off_nadir:
        return True
    else:
        return False

def is_sat_communicable(t, from_satellite: satclass.Sat, to_satellite: satclass.Sat, start_greenwich):
    from_phi, from_lam = satcompute.get_sat_geo_lat_lon(sat = from_satellite, t = t, start_greenwich = start_greenwich)

    to_phi, to_lam = satcompute.get_sat_geo_lat_lon(sat = to_satellite, t = t, start_greenwich = start_greenwich)

    # may not correct, copy from sat to ground
    theta = from_lam - to_lam
    cos_psi = math.cos(to_phi) * math.cos(from_phi) * math.cos(theta) + math.sin(to_phi) * math.sin(from_phi)
    psi = math.acos(cos_psi)
    beta = math.atan(to_satellite.r * math.sin(psi) / (from_satellite.r - satclass.Re * math.cos(psi)))  # off nadir angle, 注意atan得到的是[-pi/2,pi/2]

    off_nadir_limit = math.asin(satclass.Re/from_satellite.r)
    print(off_nadir_limit)

    if beta > off_nadir_limit:
        return True
    elif cos_psi > (to_satellite.r / from_satellite.r) and beta <= off_nadir_limit:  #when to_sat in from_sat horizon_angle and 
        return True
    else:
        return False

    # idea: find out from_sat to to_sat whether pass through the earth sphere, if yes, then the communication is false
    # method: may check by horizon line of a satellite
    # refer to https://physics.stackexchange.com/questions/151388/how-to-calculate-the-horizon-line-of-a-satellite
    # if to_sat in horizon_angle, altitude below from_sat, but from_sat.r - to_sat.r


# simulate一段时间内，卫星和地面站通信的时间段
# 输入：1.要simulate的时间段（从开始时刻0算起）
#      2.开始时刻0经度所处的赤经
#      3.卫星class
#      4.地面站class
# 输出：communication curve
def communicable(time_interval, start_greenwich, satellite: satclass.Sat, gs: gsclass.GS):
    # 根据仰角范围求off nadir角最大值
    gs_off_nadir = math.asin(satclass.Re * math.cos(gs.ele_rad) / satellite.r)
    start_ground = (math.radians(start_greenwich) + gs.long_rad) % (2 * math.pi)
    psi, phi_min, phi_max = satcompute.get_sat_phi_range(gs_off_nadir, satellite.r, gs.lat_rad)
    alpha_min1, alpha_max1, alpha_min2, alpha_max2, t_min1, t_max1, t_min2, t_max2 = satcompute.get_sat_alpha_range\
        (phi_min, phi_max, satellite)
    all_seen, gd_rang_of_alpha1, gd_rang_of_alpha2 = satcompute.get_gd_alpha_range\
        (psi, phi_min, phi_max, satellite.i_o, alpha_min1, alpha_max1, alpha_min2, alpha_max2)

    vs = []
    nvs = []
    num = math.ceil(time_interval / satellite.T_o)
    test = 0
    for n in range(num + 1):
        t1 = min(max(int(t_min1 + n * satellite.T_o), 0), time_interval)
        t2 = min(max(t_max1 + n * satellite.T_o, 0), time_interval)
        ground_alpha_min = (start_ground + satclass.omega_e * t1) % (2 * math.pi)
        ground_alpha_max = (start_ground + satclass.omega_e * t2) % (2 * math.pi)
        abandon = 0
        if all_seen == 1:
            abandon = 0
        elif gd_rang_of_alpha1[0] <= gd_rang_of_alpha1[1]:
            if ground_alpha_min < gd_rang_of_alpha1[0] and ground_alpha_max < gd_rang_of_alpha1[0]:
                abandon = 1
            if ground_alpha_min > gd_rang_of_alpha1[1] and ground_alpha_max > gd_rang_of_alpha1[1]:
                abandon = 1
        else:
            if gd_rang_of_alpha1[1] < ground_alpha_min < gd_rang_of_alpha1[0] \
                    and gd_rang_of_alpha1[1] < ground_alpha_max < gd_rang_of_alpha1[0] \
                    and ground_alpha_min <= ground_alpha_max:
                abandon = 1
        if t1 == t2:
            abandon = 1
        if abandon == 0:
            t = t1
            while t < t2+1:
                if is_gs_communicable(t, satellite, gs, gs_off_nadir, start_greenwich):
                    if test == 0:
                        #print('t1:', t)
                        test = 1
                        vs.append(round(t, 1))
                else:
                    if test:
                        #print('t2:', t)
                        test = 0
                        nvs.append(round(t, 1))
                t = t + 0.1

        t3 = min(max(int(t_min2 + n * satellite.T_o), 0), time_interval)
        t4 = min(max(t_max2 + n * satellite.T_o, 0), time_interval)
        ground_alpha_min = (start_ground + satclass.omega_e * t3) % (2 * math.pi)
        ground_alpha_max = (start_ground + satclass.omega_e * t4) % (2 * math.pi)
        abandon = 0
        if all_seen == 1:
            abandon = 0
        elif gd_rang_of_alpha2[0] <= gd_rang_of_alpha2[1]:
            if ground_alpha_min < gd_rang_of_alpha2[0] and ground_alpha_max < gd_rang_of_alpha2[0]:
                abandon = 1
            if ground_alpha_min > gd_rang_of_alpha2[1] and ground_alpha_max > gd_rang_of_alpha2[1]:
                abandon = 1
        else:
            if gd_rang_of_alpha2[1] < ground_alpha_min < gd_rang_of_alpha2[0] \
                    and gd_rang_of_alpha2[1] < ground_alpha_max < gd_rang_of_alpha2[0] \
                    and ground_alpha_min <= ground_alpha_max:
                abandon = 1
        if t3 == t4:
            abandon = 1
        if abandon == 0:
            t = t3
            while t < t4+1:
                if is_gs_communicable(t, satellite, gs, gs_off_nadir, start_greenwich):
                    if test == 0:
                        #print('t3:', t)
                        test = 1
                        vs.append(round(t, 1))
                else:
                    if test:
                        #print('t4:', t)
                        test = 0
                        nvs.append(round(t, 1))
                t = t + 0.1
    #print('vs:', vs)
    #print('nvs:', nvs)
    if test:
        nvs.append(round(time_interval))
    curve = []
    interval = []
    sum_t = 0
    if len(vs) == len(nvs):
        for v in range(len(vs)):
            curve.append([vs[v], nvs[v]])
            interval.append(nvs[v] - vs[v])
            sum_t = sum_t + (nvs[v] - vs[v])
    else:
        print(satellite)
        print(gs)
        print('off nadir:', gs_off_nadir)
        print('vs:', vs)
        print('nvs:', nvs)
        print("error type: vs is not equal to nvs")
        exit()
    return curve

