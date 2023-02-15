import math
from include import read_data

class SimParameter:
    off_nadir: float = -1
    package_size: float = -1
    data_rate: float = -1
    signal_speed: float = -1
    buffer_delay: float = -1
    process_delay: float = -1
    start_greenwich: float = -1

    @staticmethod
    def set_off_nadir(self, off_nadir):
        self.off_nadir = off_nadir

    @staticmethod
    def set_package_size(self, package_size):
        self.package_size = package_size

    @staticmethod
    def set_data_rate(self, data_rate):
        self.data_rate = data_rate

    @staticmethod
    def set_signal_speed(self, signal_speed):
        self.signal_speed = signal_speed

    @staticmethod
    def set_process_delay(self, process_delay):
        self.process_delay = process_delay

    @staticmethod
    def set_buffer_delay(self, buffer_delay):
        self.buffer_delay = buffer_delay

    @staticmethod
    def set_start_greenwich(self, start_greenwich):
        self.start_greenwich = start_greenwich


    @staticmethod
    def get_off_nadir(self):
        if self.off_nadir == -1:
            return math.radians(45)
        return self.off_nadir

    @staticmethod
    def get_package_size(self):
        if self.package_size == -1:
            return 56623104
        return self.package_size

    @staticmethod
    def get_data_rate(self):
        if self.data_rate == -1:
            return 530579456
        return self.data_rate

    @staticmethod
    def get_signal_speed(self):
        if self.signal_speed == -1:
            return 299792458
        return self.signal_speed

    @staticmethod
    def get_process_delay(self):
        if self.process_delay == -1:
            return 0.01
        return self.process_delay

    @staticmethod
    def get_buffer_delay(self):
        if self.buffer_delay == -1:
            return 0.05
        return self.buffer_delay

    @staticmethod
    def get_start_greenwich(self):
        if self.start_greenwich == -1:
            start_time_julian, start_greenwich = read_data.get_start_julian_time()
            return start_greenwich

        return self.start_greenwich