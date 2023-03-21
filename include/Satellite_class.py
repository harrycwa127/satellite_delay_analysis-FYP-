import math

# ---------constant value(orbit is circle)
miu = 3.9860047e14            # earth gravity (m^3/s^2)
omega_e = 2*math.pi/86400     # earth rotation(rad/s)
Re = 6371000                  # earth average radius(m)


# ---------satellite class
class Satellite(object):
    current_julian = 0   # current julian time (day)
    i_o = 0              # inclination (rad)
    Omega_o = 0          # right ascension of ascending node (rad)
    omega_o = 0          # argument of perigee (rad)
    M_o = 0              # mean anomaly (rad)
    circle_o = 0         # mean motion (revolutions per day)
    T_o = 0              # period
    a_o = 0              # Semi-major axis of satellite orbit (m)
    n_o = 0              # mean anomaly velocity (rad/s)
    r = 0                # radius of satellite at current time (m), inlcude the earth radius

    def __init__(self, current_julian, i_o, Omega_o, omega_o, M_o, circle_o, start_time_julian):
        self.current_julian = current_julian
        self.i_o = i_o
        self.Omega_o = Omega_o
        self.omega_o = omega_o
        self.circle_o = circle_o
        self.T_o = 86400/self.circle_o
        self.n_o = 2 * math.pi / self.T_o
        self.M_o = (M_o + self.n_o * (start_time_julian - current_julian) * 86400) % (2 * math.pi)
        self.a_o = (miu * self.T_o * self.T_o / 4 / math.pi / math.pi) ** (1 / 3)
        self.r = self.a_o

    def __str__(self):
        return "Omega: %s; M: %s" % (self.Omega_o, self.M_o)

