# Raspberry Pi ASCOM Alpaca driver

This is an ASCOM Alpaca driver which lets you use your Raspberry PI HQ camera in Windows based astrophotography software such as NINA or Sharpcap. The ASCOM installation on your PC will communicate over the network with this driver and make it appear like it's plugged in locally. It uses Python with LibCamera2 and AlpycaDevice. It's compatible with any Raspberry Pi running Bullseye Raspbian or later.

Currently, it will only recognise a Raspberry Pi HQ camera, however it's been coded to allow easy addition of other cameras.

It supports 
* binning
* subframes
* gain
* sensor temperature feedback
* exposure abort
* imagebytes downloads for better performance

Tested with:-
* Sharpcap
* NINA
* CCD-Ciel
* PHD2

*Note, Currently (as of 2.2) NINA always assumes RGGB bayer when it displays in the imaging tab for any ASCOM driver, not just this one. You should change NINA settings to force BGGR for HQ camera. However, regardless of the settings, the output FITS files will always be correct*

To get this driver to work, clone this repo onto your Raspberry pi and install the dependencies below.

```
pip3 install falcon toml orjson
apt-get install python3-picamera2 python3-lxml python3-astropy
```

Then run "python app.py".

Back on your Windows PC, run the ASCOM Diagnostics, then "Choose and Connect to a Device", Select "Camera" from the dropdown, then use the Alpaca menu to turn on Alpaca device discovery. It should then find the Raspberry PI camera and offer to install it for you. From that point onwards, you can just select it in NINA or PHD2 like you would any other ASCOM driver

This project was made possible by the ASCOM AlpycaDevice SDK https://github.com/ASCOMInitiative/AlpycaDevice and the Python Picamera2 SDK https://github.com/raspberrypi/picamera2
