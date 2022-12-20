import math

# ---------constant value(orbit is circle)
miu = 3.9860047e14            # 地球引力常数(m^3/s^2)
omega_e = 2*math.pi/86400     # 地球转速(rad/s)
Re = 6371000                  # 地球的平均半径


# ---------satellite class
class Sat(object):
    current_julian = 0   # current julian time (day)
    i_o = 0              # inclination (rad)
    Omega_o = 0          # right ascension of ascending node (rad)
    e_o = 0              # eccentricity
    omega_o = 0          # argument of perigee (rad)
    M_o = 0              # mean anomaly (rad)
    circle_o = 0         # mean motion (revolutions per day)
    T_o = 0              # period
    a_o = 0              # # 卫星轨道半长轴a (m)
    n_o = 0              # mean anomaly velocity (rad/s)
    r = 0                # radius of satellite at current time (m)

    def __init__(self, current_julian, i_o, Omega_o, e_o, omega_o, M_o, circle_o, start_time_julian):
        self.current_julian = current_julian
        self.i_o = i_o
        self.Omega_o = Omega_o
        self.e_o = e_o
        self.omega_o = omega_o
        self.circle_o = circle_o
        self.T_o = 86400/self.circle_o
        self.n_o = 2 * math.pi / self.T_o  # 平均角速率 (rad/s)
        # 设定的开始时刻时的平近点角，即卫星位置
        self.M_o = (M_o + self.n_o * (start_time_julian - current_julian) * 86400) % (2 * math.pi)
        self.a_o = (miu * self.T_o * self.T_o / 4 / math.pi / math.pi) ** (1 / 3)
        self.r = self.a_o

    def __str__(self):
        return "Omega: %s; M: %s" % (self.Omega_o, self.M_o)


# ---------virtual satellite
class VirSAT(object):
    sid = -1                       # satellite id
    vir_sid = -1                   # virtual satellite id (把一个卫星划分成了多个‘虚拟卫星’)
    lst_id = -1
    service_curve = []
    offset_list = []              # the offset list for the virtual satellite
    request_id = []               # the request id of request curve that the virtual satellite serve
    inter_len = 0                 # the intersect length for selected offset

    def __init__(self, sid, vir_sid, service_curve):
        self.sid = sid
        self.vir_sid = vir_sid
        self.service_curve = service_curve

