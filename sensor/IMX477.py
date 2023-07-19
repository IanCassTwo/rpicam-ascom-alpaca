from sensor.sensor import Sensor
from sensor.bayeroffset import BayerOffset

class IMX477(Sensor):
    def __init__(self):
        super().__init__(
            'imx477',                           # Name
            4056,                               # X Resolution
            3040,                               # Y Resolution 
            2,                                  # Binning. Sensor must have a resolution equal to resolution divided by this number
            1.55,                               # pixel size
            1,                                  # min gain
            22,                                 # max gain
            0.00006,                            # min exposure (secs)
            600,                                # max exposure (secs)
            0.469,                              # Electrons per ADU. No idea if this is right or not
            8180,                               # Full Well Capacity
            'SRGGB12',                          # unpacked RAW format
            BayerOffset.create_instance('BGGR') # Bayer Pattern
            )