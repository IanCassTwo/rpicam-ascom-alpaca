from picamera2 import Picamera2
from logging import Logger
from sensor.sensor import Sensor
from sensor.IMX477 import IMX477

class SensorFactory:
    _sensor_mapping = {
        "imx477": IMX477(),
        # TODO Add more here
    }

    @staticmethod
    def get_sensor():
        cameras = Picamera2.global_camera_info()

        if len(cameras) == 0:
            raise Exception("No cameras found!")

        # Even though we can return multiple cameras, we're only interested
        # in the first. Pi's only have one CSI port
        for c, camera in enumerate(cameras):
            s = SensorFactory._sensor_mapping.get(camera['Model'])
            if s:
                return s
            else:
                raise Exception(f"Unknown camera {camera['Model']}")