# Raspberry Pi ASCOM Alpaca driver

This is a very early version that's hard-coded for Raspberry Pi HQ camera. It supports binning and gain controls. It seems to work in NINA, CCD-Ciel and PHD2, but not in Sharpcap. It also supports binary downloads for the images as well as JSON so it's reasonably quick.

To get it to work, clone this repo onto your Raspberry pi and install the dependencies below.

pip3 install falcon toml orjson
apt-get install python3-picamera2 python3-lxml python3-astropy

Then run "python app.py".

Back on your Windows PC, run the ASCOM Diagnostics, then "Choose and Connect to a Device", Select "Camera" from the dropdown, then use the Alpaca menu to turn on Alpaca device discovery. It should then find the Raspberry PI camera and offer to install it for you. From that point onwards, you can just select it in NINA or PHD2 like you would any other ASCOM driver

This project was made using the ASCOM AlpycaDevice SDK https://github.com/ASCOMInitiative/AlpycaDevice and the Picamera2 https://github.com/raspberrypi/picamera2
