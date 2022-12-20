# ---------request class
class Request(object):
    offset = 0
    period = 0
    postponement = 0
    length = 0

    def __init__(self, offset, period, postponement, length):
        self.offset = offset
        self.period = period
        self.postponement = postponement
        self.length = length

