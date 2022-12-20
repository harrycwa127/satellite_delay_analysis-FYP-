import math
import datetime


# 根据输入的年份和天数计算对应的年月日
# 输入：年，当前是该年的第几天
# 输出：当前的年月日
def out_date_by_day(year, day):
    first_day = datetime.datetime(year, 1, 1)
    add_day = datetime.timedelta(days=day-1)
    return datetime.datetime.strftime(first_day+add_day, "%Y.%m.%d")


# 儒略日计算
# 输入：年月日以及时间（当前时刻占24小时的比例，如12点则为0.5）
# 输出：当前时刻的儒略日
def julian1(year, month, day, time):   # time指的是TLE中的表示时刻的数据的小数点部分
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
    JDE = float(J + time)
    return JDE


# 儒略日计算
# 输入：年月日时分秒
# 输出：当前时刻的儒略日
def julian2(year, month, day, hour, min, sec):
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


# Greenwich Mean Sidereal Time 格林尼治恒星时
# 输入： 当前时刻的儒略日
# 输出： 当前时刻的格林尼治恒星时（单位为度）
def greenwich(jd):
    T = (jd-2451545.0)/36525
    return 280.46061837+360.98564736629*(jd-2451545.0)+0.000387933*T*T-T*T*T/38710000



