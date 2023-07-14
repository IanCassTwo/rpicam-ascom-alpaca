from enum import Enum

class CameraState(Enum):
    IDLE = 0        # CameraIdle At idle state, available to start exposure
    WAITING = 1     # CameraWaiting Exposure started but waiting (for shutter, trigger, filter wheel, etc.)
    EXPOSING = 2    # CameraExposing Exposure currently in progress
    READING = 3     # CameraReading CCD array is being read out (digitized)
    DOWNLOADING = 4 # CameraDownload Downloading data to PC
    ERROR = 5       # CameraError Camera error condition serious enough to prevent further operations (connection fail, etc.).