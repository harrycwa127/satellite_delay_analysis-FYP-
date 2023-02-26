import math
from include import read_data

class SimParameter:
    _off_nadir: float = -1
    _package_size: float = -1
    _data_rate: float = -1
    _signal_speed: float = -1
    _buffer_delay: float = -1
    _process_delay: float = -1
    _start_greenwich: float = -1

    @classmethod
    def set_off_nadir(cls, off_nadir):
        cls._off_nadir = off_nadir

    @classmethod
    def set_package_size(cls, package_size):
        cls._package_size = package_size

    @classmethod
    def set_data_rate(cls, data_rate):
        cls._data_rate = data_rate

    @classmethod
    def set_signal_speed(cls, signal_speed):
        cls._signal_speed = signal_speed

    @classmethod
    def set_process_delay(cls, process_delay):
        cls._process_delay = process_delay

    @classmethod
    def set_buffer_delay(cls, buffer_delay):
        cls._buffer_delay = buffer_delay

    @classmethod
    def set_start_greenwich(cls, start_greenwich):
        cls._start_greenwich = start_greenwich


    @classmethod
    def get_off_nadir(cls):
        if cls._off_nadir == -1:
            return math.radians(45)
        return cls._off_nadir

    @classmethod
    def get_package_size(cls):
        if cls._package_size == -1:
            return 56623104
        return cls._package_size

    @classmethod
    def get_data_rate(cls):
        if cls._data_rate == -1:
            return 530579456
        return cls._data_rate

    @classmethod
    def get_signal_speed(cls):
        if cls._signal_speed == -1:
            return 299792458
        return cls._signal_speed

    @classmethod
    def get_process_delay(cls):
        if cls._process_delay == -1:
            return 0.01
        return cls._process_delay

    @classmethod
    def get_buffer_delay(cls):
        if cls._buffer_delay == -1:
            return 0.05
        return cls._buffer_delay

    @classmethod
    def get_start_greenwich(cls):
        if cls._start_greenwich == -1:
            start_time_julian, start_greenwich = read_data.get_start_julian_time()
            return start_greenwich

        return cls._start_greenwich