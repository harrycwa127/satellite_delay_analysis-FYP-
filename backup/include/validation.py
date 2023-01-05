from include.Satellite_class import *
from include.requestclass import *
from backup.include.voteclass import *
from include import curve
from typing import List

# given a service curve, derive the list of virtual satellites
# input: a service curve [[[a, b], [c,d]],[[e, f], [g, h]]]
# output: vs_list (the list of virtual satellites)
def init_vs_list(service_curve: List[List[List[float]]]):
    vs_list = []
    length = len(service_curve)
    index = 0
    for i in range(length):
        i_length = len(service_curve[i])
        for j in range(i_length):
            vs = VirSAT(i, j, service_curve[i][j])
            vs.lst_id = index
            vs_list.append(vs)
            index = index+1
    return vs_list


# given period and postponement of request curve, and a list of virtual satellite
# derive the offset list and corresponding request id
# assume that the offset of request curve is 0
def compute_vs_list(period, postponement, vs_list: List[VirSAT], cost):
    for i in range(len(vs_list)):
        vs = vs_list[i]
        serve_start = vs.service_curve[0]
        serve_end = vs.service_curve[1]
        if serve_end - serve_start < cost:  # service time不足以拍一张照
            continue
        rid = int(serve_start / period)
        b = [rid * period, rid * period + postponement]
        c = [(rid + 1) * period, (rid + 1) * period + postponement]
        if curve.is_intersect_cost(b, vs.service_curve, cost):
            if rid - 1 >= 0:
                a = [(rid - 1) * period, (rid - 1) * period + postponement]
                a_min = min(serve_start - a[1] + cost, period)
                a_max = min(serve_end - a[0] - cost, period)
                if a_min != period:
                    vs.offset_list = vs.offset_list+[[a_min, a_max]]
                    vs.request_id = vs.request_id+[rid - 1]
            if serve_end - b[0] - cost >= 0:
                vs.offset_list = vs.offset_list+[[0, min(serve_end - b[0] - cost, period)]]
                vs.request_id = vs.request_id+[rid]
            continue
        if curve.is_intersect_cost(c, vs.service_curve, cost):
            b_min = min(serve_start - b[1] + cost, period)
            b_max = min(serve_end - b[0] - cost, period)
            if b_min != period:
                vs.offset_list = vs.offset_list+[[b_min, b_max]]
                vs.request_id = vs.request_id+[rid]
            if serve_end - c[0] - cost >= 0:
                vs.offset_list = vs.offset_list+[[0, min(serve_end - c[0] - cost, period)]]
                vs.request_id = vs.request_id+[rid + 1]
            continue
        vs.offset_list = vs.offset_list+[[min(serve_start-b[1]+cost, period), min(serve_end-b[0]-cost, period)]]
        vs.request_id = vs.request_id+[rid]


# given a list of virtual satellite, get the offset list of all the virtual satellites
def get_all_offset(vs_list: List[VirSAT]):
    offset_list = []
    for i in range(len(vs_list)):
        vs = vs_list[i]
        offset_list = offset_list + vs.offset_list
    return offset_list


# check whether an item is in a list
def is_in_list(item, l: List[float]):
    for i in range(len(l)):
        if item == l[i]:
            return True
    return False


def get_vote_list(service_curve: List[List[List[float]]], request: Request, service_cost):
    vs_list = init_vs_list(service_curve)
    compute_vs_list(request.period, request.postponement, vs_list, service_cost)
    offset_list = get_all_offset(vs_list)

    lt = []
    for i in range(len(offset_list)):
        lt = lt + offset_list[i]
    lt = list(set(lt))
    lt.sort()
    vote_list = []
    # 初始化每个投票区间
    for j in range(len(lt)):
        if j == 0:
            vt = VOTE([lt[0], lt[0]])
            vote_list = vote_list+[vt]
        else:
            vt = VOTE([lt[j-1], lt[j]])
            vote_list = vote_list+[vt]
            vt = VOTE([lt[j], lt[j]])
            vote_list = vote_list+[vt]
    # 对每个虚拟卫星，遍历一遍投票区间进行投票
    for si in range(len(vs_list)):
        for oi in range(len(vs_list[si].offset_list)):
            offset_i = vs_list[si].offset_list[oi]
            request_i = vs_list[si].request_id[oi]
            # 遍历整个投票区间，进行投票
            for vi in range(len(vote_list)):
                # 由于投票区间是连续有序的，因此若虚拟卫星的offset scope在某个投票区间前面，那么此后的区间也绝不可能相交
                if offset_i[1] < vote_list[vi].vote_scope[0]:
                    break
                else:
                    # 若与投票区间相交，则投票
                    if offset_i[0] <= vote_list[vi].vote_scope[0] <= vote_list[vi].vote_scope[1] <= offset_i[1]:
                        vote_list[vi].sat_record = vote_list[vi].sat_record+[[si, vs_list[si].sid, request_i]]
                        # 若request_i还没被serve，则计票
                        if not is_in_list(request_i, vote_list[vi].served_request):
                            vote_list[vi].vote_num = vote_list[vi].vote_num+1
                            vote_list[vi].served_request = vote_list[vi].served_request+[request_i]
    return vote_list


def validation_by_vote(vote_list: List[VOTE], request_num, sat_num):  # 之后可以改进，这里是虚拟卫星个数最小
    vote_list_id = -1
    min_sel_real_sat_num = sat_num+1   # 避免有卫星全选的情况，所以初始化最小值时加1
    final_selected_vs = []
    final_selected_s = []
    for i in range(len(vote_list)):
        if len(vote_list[i].served_request) >= request_num:    # 所有的requests被服务
            selected_vs = []                       # selected virtual satellites list
            selected_s = []                        # selected real satellites list
            temp_sat = [0 for x in range(sat_num)]
            temp_req = [[] for x in range(request_num)]
            sat_record = vote_list[i].sat_record
            for j in range(len(sat_record)):
                vs_index = sat_record[j][0]   # 在vs_list里的id
                s_index = sat_record[j][1]
                req_index = sat_record[j][2]
                temp_sat[s_index] = temp_sat[s_index]+1
                temp_req[req_index] = temp_req[req_index]+[[s_index, vs_index]]
            temp_req.sort(key=lambda x: len(x))  # 排序保证一对一的情况都在前面
            for k in range(len(temp_req)):
                k_request = temp_req[k]
                k_request_len = len(k_request)
                if k_request_len == 1:   # 一对一的情况
                    s_id = temp_req[k][0][0]
                    vs_id = temp_req[k][0][1]
                    selected_vs.append(vs_id)
                    if not is_in_list(s_id, selected_s):
                        selected_s.append(s_id)
                else:                      # request 对多的情况
                    max_sat_to_req = 0
                    s_id = -1
                    vs_id = -1
                    flag = 0          # 这一轮已选择的标志
                    for p in range(k_request_len):
                        p_k_request = k_request[p]
                        p_s_id = p_k_request[0]
                        p_vs_id = p_k_request[1]
                        if is_in_list(p_s_id, selected_s):   # 若对应的真实卫星已在选择队列
                            selected_vs.append(p_vs_id)
                            flag = 1
                            break
                        else:
                            if temp_sat[p_s_id] > max_sat_to_req:
                                max_sat_to_req = temp_sat[p_s_id]
                                s_id = p_s_id
                                vs_id = p_vs_id
                    if not flag:
                        selected_s.append(s_id)
                        selected_vs.append(vs_id)
            selected_real_sat_num = len(selected_s)
            if selected_real_sat_num < min_sel_real_sat_num:
                min_sel_real_sat_num = selected_real_sat_num
                vote_list_id = i
                final_selected_vs = selected_vs
                final_selected_s = selected_s
    if vote_list_id != -1:   # 有解
        return True, min_sel_real_sat_num, final_selected_vs, final_selected_s
    return False, min_sel_real_sat_num, final_selected_vs, final_selected_s


def validation_by_vote_simple(vote_list: List[VOTE], request_num, sat_num):
    for i in range(len(vote_list)):
        if len(vote_list[i].served_request) >= request_num:  # 所有的requests被服务
            print("vote_scope:", vote_list[i].vote_scope)
            return True
    return False

