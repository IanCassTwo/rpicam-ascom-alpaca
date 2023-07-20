from sensor.sensor import Sensor
from sensor.bayeroffset import BayerOffset

class IMX477(Sensor):
    def __init__(self):
        super().__init__(
            'imx477',                               # Name
            4056,                                   # X Resolution
            3040,                                   # Y Resolution 
            16,                                     # Bits per pixel. Note, even though the sensor is 12bits, we're sending as 16
            2,                                      # Binning. Sensor must have a resolution equal to resolution divided by this number
            1.55,                                   # Native pixel size
            2,                                      # Max gain. Min gain is always zero
            0.00006,                                # Min exposure (secs)
            600,                                    # Max exposure (secs)
            [4.7,3.7,2.6,2.0,1.4,                   # Electrons per ADU. This should be an array of size 0 to <max gain>.                
             1.1,0.9,0.8,0.7,0.6,                   # Find the e/ADU values from Sharpcap sensor analysis
             0.6,0.5,0.4,0.4,0.3,
             0.3,0.3,0.3,0.3,0.3,
             0.2,0.2],                            
            [19403, 18370, 17350, 16342, 15347,     # Full well capacity. This should be an array of size 0 to <max gain>.
             14363, 13391, 12431, 11483, 10547,     # Fine the full well capacity values from Sharpcap sensor analysis
             9623, 8711, 7811, 6923, 6047, 
             5183, 4331, 3491, 2663, 1847, 
             1043, 251, 1134],
            'SRGGB12',                              # unpacked RAW format
            BayerOffset.create_instance('BGGR')     # Bayer Pattern                   
        )