import math

# input：Datetime
# output：julian
def julian(year, month, day, hour, min, sec):
    if month == 1 or month == 2:
        f = year - 1
        g = month + 12
    if month >= 3:
        f = year
        g = month
    mid1 = math.floor(365.25 * f)
    mid2 = math.floor(30.6001 * (g + 1))
    A = 2 - math.floor(f / 100) + math.floor(f / 400)
    J = mid1 + mid2 + day + A + 1720994.5
    JDE = float(J+hour/24+min/1440+sec/86400)
    return JDE


# Greenwich Mean Sidereal Time
# 输入： julian day
# 输出： Greenwich
def greenwich(jd):
    T = (jd-2451545.0)/36525
    return 280.46061837+360.98564736629*(jd-2451545.0)+0.000387933*T*T-T*T*T/38710000



