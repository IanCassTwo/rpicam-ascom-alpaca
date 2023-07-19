from sensor.sensor import Sensor
from sensor.bayeroffset import BayerOffset

class IMX477(Sensor):
    def __init__(self):
        super().__init__(
            'imx477',                               # Name
            4056,                                   # X Resolution
            3040,                                   # Y Resolution 
            12,                                     # Bits per pixel. Must be common across binning modes
            2,                                      # Binning. Sensor must have a resolution equal to resolution divided by this number
            1.55,                                   # native pixel size
            1,                                      # min gain
            22,                                     # max gain
            0.00006,                                # min exposure (secs)
            600,                                    # max exposure (secs)
            5.42,                                   # TODO Electrons per ADU. No idea if this is right or not. Technically it will change according to gain
            22200,                                  # TODO Full Well Capacity. Once again, this will change according to gain
            'SRGGB12',                              # unpacked RAW format
            BayerOffset.create_instance('BGGR')     # Bayer Pattern                   
        )