
# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
# camera.py - Alpaca API responder for Raspberry Pi Camera
#
# Author:   Ian Cass <ian@wheep.co.uk> https://astro.wheep.co.uk
#
# -----------------------------------------------------------------------------
# Edit History:
#   Generated by Python Interface Generator for AlpycaDevice
#
# 10/07/2023   Initial edit

from falcon import Request, Response, HTTPBadRequest, before
from logging import Logger
from shr import ImageArrayResponse, PropertyResponse, MethodResponse, PreProcessRequest, \
                get_request_field, to_bool #, to_int, to_float
from exceptions import *        # Nothing but exception
from picamera2 import Picamera2
from camerastate import CameraState
from sensor.SensorFactory import SensorFactory
from state import State
import libcamera
import numpy as np
import threading

logger: Logger = None
state = State()
sensor = None

# ----------------------
# MULTI-INSTANCE SUPPORT
# ----------------------
# If this is > 0 then it means that multiple devices of this type are supported.
# Each responder on_get() and on_put() is called with a devnum parameter to indicate
# which instance of the device (0-based) is being called by the client. Leave this
# set to 0 for the simple case of controlling only one instance of this device type.
#
maxdev = 0                      # Single instance

# -----------
# DEVICE INFO
# -----------
# Static metadata not subject to configuration changes
class CameraMetadata:
    Name = 'Raspberry Pi Camera'
    Version = 'v0.01'
    Description = 'A Raspberry Pi Camerai using Libcamera'
    DeviceType = 'Camera'
    DeviceID = '0584a99f-0c46-4e27-a312-e2a93dbc65e2'
    Info = 'Alpaca Device\nImplements ICamera\nASCOM Initiative'
    MaxDeviceNumber = maxdev
    InterfaceVersion = 3        # ICameraV3

# Camera Init
picam2 = None
def start_camera_device(logger: logger):
    logger = logger

    # Set up sensor & state defaults
    global sensor 
    sensor = SensorFactory.get_sensor()
    state.num_x = sensor.get_size_x()
    state.num_y = sensor.get_size_y()
    
    # Initialize PiCamera2
    global picam2
    picam2 = Picamera2()

# RESOURCE CONTROLLERS
@before(PreProcessRequest(maxdev))
class Action:
    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = MethodResponse(req, NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class CommandBlind:
    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = MethodResponse(req, NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class CommandBool:
    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = MethodResponse(req, NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class CommandString():
    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = MethodResponse(req, NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class Description():
    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(CameraMetadata.Description, req).json

@before(PreProcessRequest(maxdev))
class DriverInfo():
    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(CameraMetadata.Info, req).json

@before(PreProcessRequest(maxdev))
class InterfaceVersion():
    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(CameraMetadata.InterfaceVersion, req).json

@before(PreProcessRequest(maxdev))
class DriverVersion():
    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(CameraMetadata.Version, req).json

@before(PreProcessRequest(maxdev))
class Name():
    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(CameraMetadata.Name, req).json

@before(PreProcessRequest(maxdev))
class SupportedActions():
    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse([], req).json  # Not PropertyNotImplemented

@before(PreProcessRequest(maxdev))
class bayeroffsetx:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        try:

            resp.text = PropertyResponse(sensor.get_bayer_pattern().get_offset_x(), req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                            DriverException(0x500, 'Camera.Bayeroffsetx failed', ex)).json

@before(PreProcessRequest(maxdev))
class bayeroffsety:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        try:
            resp.text = PropertyResponse(sensor.get_bayer_pattern().get_offset_y(), req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                            DriverException(0x500, 'Camera.Bayeroffsety failed', ex)).json

@before(PreProcessRequest(maxdev))
class binx:

    def on_get(self, req: Request, resp: Response, devnum: int):

        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        try:            
            resp.text = PropertyResponse(state.binning, req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                            DriverException(0x500, 'Camera.Binx failed', ex)).json


    def on_put(self, req: Request, resp: Response, devnum: int):
     
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        binxstr = get_request_field('BinX', req)      # Raises 400 bad request if missing
        try:
            binx = int(binxstr)
        except:
            resp.text = MethodResponse(req,
                            InvalidValueException(f'BinX {binxstr} not a valid number.')).json
            return
        ### RANGE CHECK
        if binx < 1 or binx > 2:
            resp.text = MethodResponse(req,
                            InvalidValueException(f'BinX {binxstr} not in range')).json
            return
        try:
            # Set device mode            
            if binx != state.binning:
                # Binning mode has changed, switch camera resolution
                state.binning = binx
                config = picam2.create_still_configuration( {"size": (640, 480)}, queue=False, buffer_count=2,  raw={'format': sensor.get_raw_format(),'size': (int(sensor.get_size_x() / state.binning), int(sensor.get_size_y() / state.binning))})
                picam2.stop()
                picam2.configure(config)
                picam2.start()

            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                            DriverException(0x500, 'Camera.Binx failed', ex)).json


@before(PreProcessRequest(maxdev))
class biny(binx):

    def on_get(self, req: Request, resp: Response, devnum: int):
                super().on_get(req, resp, devnum)

    def on_put(self, req: Request, resp: Response, devnum: int):
     
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        binxstr = get_request_field('BinY', req)      # Raises 400 bad request if missing
        try:
            binx = int(binxstr)
        except:
            resp.text = MethodResponse(req,
                            InvalidValueException(f'BinY {binxstr} not a valid number.')).json
            return
        ### RANGE CHECK
        if binx < 1 or binx > 2:
            resp.text = MethodResponse(req,
                            InvalidValueException(f'BinY {binxstr} not in range')).json
            return
        try:
            # Set device mode            
            if binx != state.binning:
                # Binning mode has changed, switch camera resolution
                state.binning = binx
                config = picam2.create_still_configuration( {"size": (640, 480)}, queue=False, buffer_count=2,  raw={'format': sensor.get_raw_format(),'size': (int(sensor.get_size_x() / state.binning), int(sensor.get_size_y() / state.binning))})
                picam2.stop()
                picam2.configure(config)
                picam2.start()
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                            DriverException(0x500, 'Camera.Biny failed', ex)).json

@before(PreProcessRequest(maxdev))
class camerastate:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        try:
            # ----------------------
            # Returns one of the following status information:
            # 0 CameraIdle At idle state, available to start exposure
            # 1 CameraWaiting Exposure started but waiting (for shutter, trigger, filter wheel, etc.)
            # 2 CameraExposing Exposure currently in progress
            # 3 CameraReading CCD array is being read out (digitized)
            # 4 CameraDownload Downloading data to PC
            # 5 CameraError Camera error condition serious enough to prevent further operations (connection fail, etc.).
            # ----------------------
            resp.text = PropertyResponse(state.camerastate.value, req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                            DriverException(0x500, 'Camera.Camerastate failed', ex)).json

@before(PreProcessRequest(maxdev))
class cameraxsize:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        resp.text = PropertyResponse(sensor.get_size_x(), req).json

@before(PreProcessRequest(maxdev))
class cameraysize:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        resp.text = PropertyResponse(sensor.get_size_y(), req).json

@before(PreProcessRequest(maxdev))
class canabortexposure:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(True, req).json

@before(PreProcessRequest(maxdev))
class canasymmetricbin:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(False, req).json

@before(PreProcessRequest(maxdev))
class canfastreadout:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(False, req).json


@before(PreProcessRequest(maxdev))
class cangetcoolerpower:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(False, req).json


@before(PreProcessRequest(maxdev))
class canpulseguide:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(False, req).json


@before(PreProcessRequest(maxdev))
class cansetccdtemperature:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(False, req).json

@before(PreProcessRequest(maxdev))
class canstopexposure:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(False, req).json

@before(PreProcessRequest(maxdev))
class ccdtemperature:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                        NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class cooleron:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                        NotImplementedException()).json

    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class coolerpower:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                    NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class electronsperadu:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        try:
            resp.text = PropertyResponse(sensor.get_electrons_per_adu(), req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                            DriverException(0x500, 'Camera.Electronsperadu failed', ex)).json

@before(PreProcessRequest(maxdev))
class exposuremax:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        try:
            resp.text = PropertyResponse(sensor.get_max_exposure(), req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                            DriverException(0x500, 'Camera.Exposuremax failed', ex)).json

@before(PreProcessRequest(maxdev))
class exposuremin:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        try:
            resp.text = PropertyResponse(sensor.get_min_exposure(), req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                            DriverException(0x500, 'Camera.Exposuremin failed', ex)).json

@before(PreProcessRequest(maxdev))
class exposureresolution:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(0.0, req).json


@before(PreProcessRequest(maxdev))
class fastreadout:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class fullwellcapacity:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        try:
            resp.text = PropertyResponse(sensor.get_full_well_capacity(), req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                            DriverException(0x500, 'Camera.Fullwellcapacity failed', ex)).json

@before(PreProcessRequest(maxdev))
class gain:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        resp.text = PropertyResponse(state.gainvalue, req).json

    def on_put(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        gainstr = get_request_field('Gain', req)      # Raises 400 bad request if missing
        try:
            g = int(gainstr)
        except:
            resp.text = MethodResponse(req,
                            InvalidValueException(f'Gain {gainstr} not a valid number.')).json
            return
        ### RANGE CHECK
        if g < sensor.get_min_gain() or g > sensor.get_max_gain():
                resp.text = MethodResponse(req,
                            InvalidValueException(f'Gain {gainstr} is out of bounds.')).json
                return
        try:
            ### DEVICE OPERATION(PARAM) ###
            if state.gainvalue != g:
                state.gainvalue = g
                state.need_restart = True
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                            DriverException(0x500, 'Camera.Gain failed', ex)).json

@before(PreProcessRequest(maxdev))
class gainmax:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        try:
            resp.text = PropertyResponse(sensor.get_max_gain(), req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                            DriverException(0x500, 'Camera.Gainmax failed', ex)).json

@before(PreProcessRequest(maxdev))
class gainmin:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return

        resp.text = PropertyResponse(sensor.get_min_gain(), req).json

@before(PreProcessRequest(maxdev))
class gains:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class hasshutter:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        resp.text = PropertyResponse(False, req).json


@before(PreProcessRequest(maxdev))
class heatsinktemperature:
    # FIXME I think we can get this from image metadata. However, we're not retrieving metadata at the moment
    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class imagearray:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        
        if not state.imageReady:
            resp.text = PropertyResponse(None, req,
                            InvalidOperationException()).json
            return
        
        try:
            #array = picam2.wait(state.job).view(np.uint16) * (2 ** (16 - 12))
            # ChatGPT says this is quicker
            array = picam2.wait(state.job).view(np.uint16) * np.left_shift(1, (16 - 12))

            state.imageReady = False # We've grabbed the image now

            # Resize array to correct frame size according to max resolution and subframe settings
            array = array[state.start_y:state.start_y + state.num_y, state.start_x:state.start_x + state.num_x]
            array = np.transpose(array)

            accept = req.headers.get("ACCEPT")
            if accept is not None and 'imagebytes' in accept:
                # ImageBytes

                # Create response
                logger.debug("Creating ImageArrayResponse")
                pr = ImageArrayResponse(array, req)                
                resp.data = pr.binary
                resp.content_type = 'application/imagebytes'
                logger.debug("Created ImageArrayResponse")

            else:
                # JSON - warning, this is speed optimized but it still much slower than imagebytes!

                # Convert array to a list of tuples, where each tuple is a column
                array = list(map(tuple, array.astype(int).tolist()))

                # Create response
                logger.debug("Creating ImageArrayResponse")
                pr = ImageArrayResponse(array, req)
                resp.text = pr.json 
                resp.content_type = 'application/json'
                logger.debug("Created ImageArrayJsonResponse")
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                            DriverException(0x500, 'Camera.Imagearray failed', ex)).json

@before(PreProcessRequest(maxdev))
class imagearrayvariant(imagearray):
    def on_get(self, req: Request, resp: Response, devnum: int):
        super().on_get(req, resp, devnum)

def oncapturefinished(Job):
    state.camerastate = CameraState.IDLE
    state.imageReady = True
    logger.debug("oncapturefinished")

@before(PreProcessRequest(maxdev))
class imageready:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return

        resp.text = PropertyResponse(state.imageReady, req).json


@before(PreProcessRequest(maxdev))
class ispulseguiding:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class lastexposureduration:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class lastexposurestarttime:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class maxadu:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return

         # FIXME no idea but I think this is right, although for a 12bit sensor this would probably be 4095
        resp.text = PropertyResponse(65535, req).json

@before(PreProcessRequest(maxdev))
class maxbinx:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        try:
            resp.text = PropertyResponse(sensor.get_max_binning(), req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                            DriverException(0x500, 'Camera.Maxbinx failed', ex)).json

@before(PreProcessRequest(maxdev))
class maxbiny(maxbinx):

    def on_get(self, req: Request, resp: Response, devnum: int):
         super().on_get(req, resp, devnum)


@before(PreProcessRequest(maxdev))
class numx:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return

        resp.text = PropertyResponse(state.num_x, req).json

    def on_put(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        numxstr = get_request_field('NumX', req)      # Raises 400 bad request if missing
        try:
            nnum_x = int(numxstr)
        except:
            resp.text = MethodResponse(req,
                            InvalidValueException(f'NumX {numxstr} not a valid number.')).json
            return
        ### RANGE CHECK AS NEEDED ###       # Raise Alpaca InvalidValueException with details!
        if nnum_x < 0 or nnum_x > sensor.get_size_x(): # FIXME do we need to take binning into account?
            resp.text = MethodResponse(req,
                            InvalidValueException(f'NumX {numxstr} is out of bounds.')).json
            return
        try:
            ### DEVICE OPERATION(PARAM) ###
            state.num_x = nnum_x
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                            DriverException(0x500, 'Camera.Numx failed', ex)).json

@before(PreProcessRequest(maxdev))
class numy:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        resp.text = PropertyResponse(state.num_y, req).json

    def on_put(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        numystr = get_request_field('NumY', req)      # Raises 400 bad request if missing
        try:
            nnum_y = int(numystr)
        except:
            resp.text = MethodResponse(req,
                            InvalidValueException(f'NumY {numystr} not a valid number.')).json
            return
        ### RANGE CHECK AS NEEDED ###       # Raise Alpaca InvalidValueException with details!
        if nnum_y < 0 or nnum_y > sensor.get_size_y(): # FIXME do we need to take binning into account?
            resp.text = MethodResponse(req,
                            InvalidValueException(f'NumY {numystr} is out of bounds.')).json
            return
        try:
            ### DEVICE OPERATION(PARAM) ###
            state.num_y = nnum_y
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                            DriverException(0x500, 'Camera.Numy failed', ex)).json

@before(PreProcessRequest(maxdev))
class offset:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class offsetmax:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class offsetmin:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class offsets:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class percentcompleted:

    def on_get(self, req: Request, resp: Response, devnum: int):
        # FIXME perhaps we can calculate this from exposure start time?
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class pixelsizex:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        try:
            resp.text = PropertyResponse(sensor.get_pixel_size(), req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                            DriverException(0x500, 'Camera.Pixelsizex failed', ex)).json

@before(PreProcessRequest(maxdev))
class pixelsizey(pixelsizex):

    def on_get(self, req: Request, resp: Response, devnum: int):
        super().on_get(req, resp, devnum)

@before(PreProcessRequest(maxdev))
class readoutmode:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        resp.text = PropertyResponse(0, req).json

    def on_put(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        readoutmodestr = get_request_field('ReadoutMode', req)      # Raises 400 bad request if missing
        try:
            readoutmode = int(readoutmodestr)
        except:
            resp.text = MethodResponse(req,
                            InvalidValueException(f'ReadoutMode {readoutmodestr} not a valid number.')).json
            return
        ### RANGE CHECK FIXME
        try:
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                            DriverException(0x500, 'Camera.Readoutmode failed', ex)).json

@before(PreProcessRequest(maxdev))
class readoutmodes:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return

        resp.text = PropertyResponse(["default"], req).json

@before(PreProcessRequest(maxdev))
class sensorname:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        try:
            resp.text = PropertyResponse(sensor.get_name(), req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                            DriverException(0x500, 'Camera.Sensorname failed', ex)).json

@before(PreProcessRequest(maxdev))
class sensortype:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        # SensorType is always 2 = RGGB bayered images. The actual bayer pattern is specified in the bayer offset properties
        resp.text = PropertyResponse(2, req).json

@before(PreProcessRequest(maxdev))
class setccdtemperature:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class startx:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        resp.text = PropertyResponse(state.start_x, req).json

    def on_put(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        startxstr = get_request_field('StartX', req)      # Raises 400 bad request if missing
        try:
            nstart_x = int(startxstr)
        except:
            resp.text = MethodResponse(req,
                            InvalidValueException(f'StartX {startxstr} not a valid number.')).json
            return
        ### RANGE CHECK AS NEEDED ###       # Raise Alpaca InvalidValueException with details!
        if nstart_x < 0 or nstart_x > sensor.get_size_x():
            resp.text = MethodResponse(req,
                            InvalidValueException(f'StartX {startxstr} is out of bounds.')).json
            return
        try:
            ### DEVICE OPERATION(PARAM) ###
            state.start_x = nstart_x
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                            DriverException(0x500, 'Camera.Startx failed', ex)).json

@before(PreProcessRequest(maxdev))
class starty:

    def on_get(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return

        resp.text = PropertyResponse(state.start_y, req).json

    def on_put(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        startystr = get_request_field('StartY', req)      # Raises 400 bad request if missing
        try:
            nstart_y = int(startystr)
        except:
            resp.text = MethodResponse(req,
                            InvalidValueException(f'StartY {startystr} not a valid number.')).json
            return
        ### RANGE CHECK AS NEEDED ###       # Raise Alpaca InvalidValueException with details!
        if nstart_y < 0 or nstart_y > sensor.get_size_y():
            resp.text = MethodResponse(req,
                            InvalidValueException(f'StartY {startystr} is out of bounds.')).json
            return
        try:
            ### DEVICE OPERATION(PARAM) ###
            state.start_y = nstart_y
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                            DriverException(0x500, 'Camera.Starty failed', ex)).json

@before(PreProcessRequest(maxdev))
class subexposureduration:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json    

    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class abortexposure:

    def on_put(self, req: Request, resp: Response, devnum: int):
        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        try:
            if state.camerastate == CameraState.EXPOSING:
                picam2.stop_()
                state.camerastate = CameraState.IDLE
                picam2.start()
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                            DriverException(0x500, 'Camera.Abortexposure failed', ex)).json


@before(PreProcessRequest(maxdev))
class pulseguide:

    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class startexposure:

    def on_put(self, req: Request, resp: Response, devnum: int):

        if not picam2.started:
            resp.text = PropertyResponse(None, req,
                            NotConnectedException()).json
            return
        durationstr = get_request_field('Duration', req) 
        try:
            duration = float(durationstr)
        except:
            resp.text = MethodResponse(req,
                            InvalidValueException(f'Duration {durationstr} not a valid number.')).json
            return
        
        ### RANGE CHECK AS NEEDED ###
        if duration < 0 or duration > 600:
            resp.text = MethodResponse(req,
                            InvalidValueException(f'Duration {durationstr} is out of bounds')).json
            return

        if duration != state.last_duration:
            state.last_duration = duration
            state.need_restart = True

        try:
            logger.debug("Exposure duration is %f, gain is %d", duration, state.gainvalue)

            if state.need_restart:
                picam2.stop()
                with picam2.controls as controls:
                    controls.ExposureTime = int(duration * 1e6)
                    controls.AeEnable = False
                    controls.NoiseReductionMode = libcamera.controls.draft.NoiseReductionModeEnum.Off
                    controls.AwbEnable = False
                    controls.AnalogueGain = state.gainvalue
                picam2.start()
                state.need_restart = False

            state.job = picam2.capture_array("raw", signal_function=oncapturefinished)
            state.camerastate = CameraState.EXPOSING
            # -----------------------------
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                            DriverException(0x500, 'Camera.Startexposure failed', ex)).json

@before(PreProcessRequest(maxdev))
class stopexposure:

    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(None, req,
                NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class connected:

    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(picam2.started, req).json

    def on_put(self, req: Request, resp: Response, devnum: int):
        conn_str = get_request_field('Connected', req)
        conn = to_bool(conn_str)              # Raises 400 Bad Request if str to bool fails

        # start/stop
        if (conn):
            try:
                if not picam2.started:
                    config = picam2.create_still_configuration( {"size": (640, 480)}, queue=False, buffer_count=2,  raw={'format': sensor.get_raw_format(),'size': (int(sensor.get_size_x() / state.binning), int(sensor.get_size_y() / state.binning))})
                    picam2.configure(config)
                    picam2.start()
                # ----------------------
                resp.text = MethodResponse(req).json
            except Exception as ex:
                resp.text = MethodResponse(req,
                                DriverException(0x500, f'{self.__class__.__name__} failed', ex)).json

        else:  
            try:
                if picam2.started:
                    picam2.stop()
                # ----------------------
                resp.text = MethodResponse(req).json
            except Exception as ex:
                resp.text = MethodResponse(req,
                                DriverException(0x500, f'{self.__class__.__name__} failed', ex)).json