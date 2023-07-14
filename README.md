# Raspberry Pi ASCOM Alpaca driver

This is an alpha version that's hard-coded for Raspberry Pi HQ camera. It's quite usable. 

It supports 
* binning
* subframes
* gain
* imagebytes downloads for better performance

Tested with:-
* Sharpcap
* NINA
* CCD-Ciel
* PHD2

To get it to work, clone this repo onto your Raspberry pi and install the dependencies below.

pip3 install falcon toml orjson
apt-get install python3-picamera2 python3-lxml python3-astropy

Then run "python app.py".

Back on your Windows PC, run the ASCOM Diagnostics, then "Choose and Connect to a Device", Select "Camera" from the dropdown, then use the Alpaca menu to turn on Alpaca device discovery. It should then find the Raspberry PI camera and offer to install it for you. From that point onwards, you can just select it in NINA or PHD2 like you would any other ASCOM driver

This project was made possible by the ASCOM AlpycaDevice SDK https://github.com/ASCOMInitiative/AlpycaDevice and the Python Picamera2 SDK https://github.com/raspberrypi/picamera2
