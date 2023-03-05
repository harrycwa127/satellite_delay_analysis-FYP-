from include import curve
from typing import List

# compute the observation curve of satellite which satisfy the deadline restraint
# input: 1) imaging curve ([[], []]) (s)
#        2) communication curve ([[], []])(s)
#        3) imaging time cost (s)
#        4) communication time cost (s)
#        5) deadline (the time interval from imaging instant to transfer completion time) (s)
# output: the observation curve of satellite which satisfy the deadline restraint ([[], []]) (s)
def get_obs_curve(img_curve: List[List[float]], com_curve: List[List[float]], img_cost, com_cost, ddl):
    temp_curve = []
    for i in range(len(com_curve)):
        t_min = com_curve[i][0]
        t_max = com_curve[i][1]
        # 1. 该通信间隔无法满足一次通信时长的需求  2. 拍照时间加上通信时间大于deadline
        if t_max-com_cost < t_min or ddl < img_cost+com_cost:
            continue
        temp_curve.append([t_min+com_cost-ddl, t_max-com_cost-img_cost])
    obs_curve = curve.inter_curve(img_curve, temp_curve)
    return obs_curve

