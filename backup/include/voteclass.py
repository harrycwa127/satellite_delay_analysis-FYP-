from typing import List

# ---------allocation class 最终的分配为list of Alloc
class Alloc(object):
    served = 0
    sid = -1
    v_sid = -1

    def __str__(self):
        return "satellite is %s, virtual id is %s" % (self.sid, self.v_sid)


# ---------vote data structure
class VOTE(object):
    vote_scope = [-1, -1]      # 投票区间
    vote_num = 0               # 投票数
    served_request = []        # 已served的request id
    sat_record = []            # 已投票的虚拟卫星

    def __init__(self, vote_scope: List[float, float]):
        self.vote_scope = vote_scope

    def __str__(self):
        return "vote scope: %s, satellites: %s" % (self.vote_scope, self.sat_record)

