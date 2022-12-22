from include import satclass
from backup import gdclass
from include import satcompute
import math


# 判断当前时刻卫星是否能看到地面点
# 输入：1.当前时刻t（相对于开始时刻的时间）
#      2.卫星class
#      3.地面点class
#      4.off_nadir角
#      5.开始时刻0经度所处的赤经
# 输出：TRUE OR FALSE
def is_visible(t, satellite: satclass.Sat, gd: gdclass.GD, off_nadir, start_greenwich):
    M = (satellite.n_o * t + satellite.M_o) % (2 * math.pi)  # t时刻平近点角(rad)
    f = M  # 假设是圆轨道
    r = satellite.a_o  # 假设是圆轨道
    u = satellite.omega_o + f
    alpha = satcompute.sat_alpha(r, satellite.Omega_o, u, satellite.i_o)
    delta = math.asin(math.sin(u) * math.sin(satellite.i_o))  # t时刻卫星赤纬
    phi = delta  # t时刻卫星地心纬度
    lam = alpha - (math.radians(start_greenwich) + satclass.omega_e * t) % (2 * math.pi)  # t时刻卫星地心经度
    if lam > math.pi:
        lam = lam - 2 * math.pi
    if lam < -math.pi:
        lam = lam + 2 * math.pi
    theta = lam - gd.long_rad
    cos_psi = math.cos(gd.lat_rad) * math.cos(phi) * math.cos(theta) + math.sin(gd.lat_rad) * math.sin(phi)
    psi = math.acos(cos_psi)
    beta = math.atan(satclass.Re * math.sin(psi) / (r - satclass.Re * math.cos(psi)))  # off nadir angle, 注意atan得到的是[-pi/2,pi/2]
    if cos_psi > satclass.Re / r and beta <= off_nadir:
        return True
    else:
        return False


# simulate一段时间内，卫星可观测到地面点的时间段
# 输入：1.要simulate的时间段（从开始时刻0算起）
#      2.开始时刻0经度所处的赤经
#      3.卫星class
#      4.地面点class
#      5.off_nadir角
# 输出：imaging curve
def visible(time_interval, start_greenwich, satellite: satclass.Sat, gd: gdclass.GD, off_nadir):
    start_ground = (math.radians(start_greenwich) + gd.long_rad) % (2 * math.pi)
    psi, phi_min, phi_max = satcompute.get_sat_phi_range(off_nadir, satellite.a_o, gd.lat_rad)
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
                if is_visible(t, satellite, gd, off_nadir, start_greenwich):
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
                if is_visible(t, satellite, gd, off_nadir, start_greenwich):
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
        print(gd)
        print('off nadir:', off_nadir)
        print('vs:', vs)
        print('nvs:', nvs)
        print("error type: vs is not equal to nvs")
        exit()
    return curve

