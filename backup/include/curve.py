from typing import List

# 两个curve的并集
# 输入 l1: [[1, 2], [5, 6], [8, 10]]   l2: [[1, 5], [7, 12]]
# 输出 [[1, 6] [7, 12]]
# 本质: 只有当两个区间有相交, 才会合并; 如果不相交, 不合并
def merge_curve(l1: List[List[float]],  l2: List[List[float]]) -> List[List[float]]:
    lt = l1 + l2
    res = []
    # 排序, start小的在前
    lt.sort(key=lambda x: x[0])
    if lt:
        start = lt[0][0]
        end = lt[0][1]
        for i in range(1, len(lt)):
            # 相交则合并
            if lt[i][0] <= end < lt[i][1]:
                end = lt[i][1]
            # [start, end]包含了[[i][0], lt[i][1]]区间
            elif start <= lt[i][0] and end >= lt[i][1]:
                continue
            else:
                res.append([start, end])
                start = lt[i][0]
                end = lt[i][1]
        res.append([start, end])
    return res


# 两个curve交集
# 输入 l1: [[1, 2], [5, 6], [8, 10]]  l2: [[1, 5], [7, 12]]
# 输出 [[1, 2] [8, 10]]
# 由于l1 l2是有序的, 可以利用这点, 进行遍历
def inter_curve(l1: List[List[float]], l2: List[List[float]]) -> List[List[float]]:
    len1 = len(l1)
    len2 = len(l2)
    i = 0
    j = 0
    res = []
    while i < len1 and j < len2:
        # 不相交的情况, l1[i]在后面
        if l1[i][0] >= l2[j][1]:
            j = j + 1
        # 不相交的情况, l2[j]在后面
        elif l2[j][0] >= l1[i][1]:
            i = i + 1
        # 其他的都是有交集, 交集取最小的区间
        else:
            res.append([max(l1[i][0], l2[j][0]), min(l1[i][1], l2[j][1])])
            if l1[i][1] < l2[j][1]:
                i = i + 1
            else:
                j = j + 1
    return res


# 两个单区间相交部分的长度
# 输入：两个单区间，如[1,5]和[3.6]
# 输出：两个单区间相交部分的长度，上例输出为2
def intersect_length(l1: List[float, float], l2: List[float, float]):
    if l1[1] <= l2[0] or l1[0] >= l2[1]:    # not intersect
        return 0
    else:
        lt = l1+l2
        lt.sort()
        inter_len = lt[2]-lt[1]
        return inter_len


# 两个单区间相交部分的长度和区间
# 输入：两个单区间，如[1,5]和[3.6]
# 输出：两个单区间相交部分的长度，上例输出为2,[3,5]
def intersect_length_range(l1: List[float, float], l2: List[float, float]):
    if l1[1] <= l2[0] or l1[0] >= l2[1]:    # not intersect
        return 0, [-1, -1]
    else:
        lt = l1+l2
        lt.sort()
        inter_len = lt[2]-lt[1]
        return inter_len, [lt[1], lt[2]]


# 判断两个单区间是否相交且相交部分超过cost
def is_intersect_cost(l1: List[float, float], l2: List[float, float], cost):
    inter_len = intersect_length(l1, l2)
    if inter_len == 0:    # not intersect
        return False
    elif inter_len >= cost:
        return True
    else:
        return False


def get_responding_rid(imaging_curve: List[float], request_curve: List[float], period, postponement):
    rid_list = []
    for i in range(len(imaging_curve)):
        item = imaging_curve[i]
        single_rid_list = []
        range_min = int(item[0]/period)
        range_max = min(int(item[1]/period)+1, len(request_curve))
        for j in range(range_min, range_max):
            if intersect_length(item, request_curve[j]) > 0:
                single_rid_list.append(j)
        rid_list.append(single_rid_list)
    return rid_list

