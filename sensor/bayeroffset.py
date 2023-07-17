# https://ascom-standards.org/Help/Platform/html/P_ASCOM_DeviceInterface_ICameraV3_SensorType.htm
#
# Bayer offsets are both zero = RGGB
# x Bayer offset is 1 and y bayer offset is 0, GRBG.
# x Bayer offset is 0 and y bayer offset is 1, GBRG.
# both Bayer offsets are 1, BGGR.

class BayerOffset:
    offset_names = {
        "rggb": (0, 0),
        "grbg": (1, 0),
        "gbrg": (0, 1),
        "bggr": (1, 1)
    }

    @staticmethod
    def create_instance(name):
        name = name.lower()  # Convert input name to lowercase
        if name in BayerOffset.offset_names:
            offset_x, offset_y = BayerOffset.offset_names[name]
            return BayerOffsetInstance(offset_x, offset_y)
        else:
            raise ValueError("Invalid Bayer offset name")


class BayerOffsetInstance:
    def __init__(self, offset_x, offset_y):
        self.offset_x = offset_x
        self.offset_y = offset_y

    def get_offset_x(self):
        return self.offset_x

    def get_offset_y(self):
        return self.offset_y