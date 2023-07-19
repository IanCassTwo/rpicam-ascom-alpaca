from abc import ABC, abstractmethod

class Sensor(ABC):
    def __init__(self, name, size_x, size_y, bits_per_pixel, max_binning, pixel_size, min_gain, max_gain, 
                 min_exposure, max_exposure, electrons_per_adu, full_well_capacity, raw_format, bayer_pattern):
        self._name = name
        self._size_x = size_x
        self._size_y = size_y
        self._bits_per_pixel = bits_per_pixel
        self._max_binning = max_binning
        self._pixel_size = pixel_size
        self._min_gain = min_gain
        self._max_gain = max_gain
        self._min_exposure = min_exposure
        self._max_exposure = max_exposure
        self._electrons_per_adu = electrons_per_adu
        self._full_well_capacity = full_well_capacity
        self._raw_format = raw_format
        self._bayer_pattern = bayer_pattern

    def get_name(self):
        return self._name

    def get_size_x(self):
        return self._size_x

    def get_size_y(self):
        return self._size_y

    def get_max_binning(self):
        return self._max_binning

    def get_pixel_size(self):
        return self._pixel_size

    def get_min_gain(self):
        return self._min_gain

    def get_max_gain(self):
        return self._max_gain

    def get_min_exposure(self):
        return self._min_exposure

    def get_max_exposure(self):
        return self._max_exposure
    
    def get_electrons_per_adu(self):
        return self._electrons_per_adu
    
    def get_full_well_capacity(self):
        return self._full_well_capacity

    def get_raw_format(self):
        return self._raw_format
    
    def get_bayer_pattern(self):
        return self._bayer_pattern
    
    def get_bits_per_pixel(self):
        return self._bits_per_pixel
    
    def get_max_adu(self):
        return (2 ** self._bits_per_pixel) - 1