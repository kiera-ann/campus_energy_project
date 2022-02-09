# Campus Power Project

The platform developed for this study encompassed both the creation of custom hardware and software tailored for the
monitoring of electrical energy used in the student dorm setting, the execution of self-defined algorithm for estimating
the energy’s carbon intensity, and the presentation to the end user in a modern user interface.

## Description of Folders

Campus_data_code – code for calculating Princeton University Overall Campus Electricity based CO2

ESP32_MQTT_Code – code to handle ESP 32 Microcontroller data flow (data request publish and retrieval of published data)

PJM_code – code to get grid data for the state of NJ and parse for use in this platform

flask_backend - Python Flask backend that serves data to React Frontend

react_frontend – React JS Frontend to touchscreen kiosk (co-written with another UG student at Princeton)

arduino_MCU_code – Arduino code ran on the microcontrollers to connect to University WiFi network and publish sensor data
when sensor data is requested from server hosted in dorm running code in "ESP32_MQTT_Code"

Project_images - Contains images taken during development of hardware and software for project. Sub-folders include
i) Hardware – IoT devices
<img width=“964” alt=“enviro sensor” src=“https://github.com/kiera-ann/campus_energy_project/blob/master/Project_images/Hardware/Enviro%20Sensor%20Enclosure%20annotated.tiff”>

ii) Project Background – General Campus Energy Introduction
iii) System Design – Top level view of interconnections between hardware and software
iv) User Interface - Annotated UI shown on Raspberry Pi Screen Kiosk

## Docker

A number of Docker programs were run for this project

InfluxDB (timeseries database)
InfluxDB Terminal Commands in Docker:

### `docker pull influxdb:1.8.4`

### `docker run -d --name influxdb_1.8.4 -p 8086:8086 influxdb:1.8.4`

MQTT for Machine to Machine Communication (for microcontrollers)
MQTT Terminal Commands in Docker:

### `docker pull eclipse-mosquitto:1.6.12`

### `docker run -it -p 1883:1883 --name eclipse-mosquitto_1.6.12 eclipse- mosquitto:1.6.12`

## Setup Instructions for Raspberry PI based touchscreen Kiosk

### `sudo pip3 install rpi-backlight $ sudo rpi-backlight-gui`

After, the kiosk mode was set up entering the following command in Terminal.

### `sudo nano /etc/xdg/lxsession/LXDE-pi/autostart`

Then, the following block of text was written and saved to the “autostart” file:

### `@xset s noblank @xset s off @xset -dpms @lxpanel --profile LXDE-pi @pcmanfm --desktop --profile LXDE-pi @xscreensaver -no-splash /usr/bin/chromium-browser --kiosk --disable-restore-session-state http://140.180.133.174:5000/$$`

where $$ is specific to the user account. For example, $$ could be "a5" which represents “aware user number 5”.

Aware was the terminology used in this study to mean users who were provided kiosks and MCU current sensors. This is
because only some users were in this cohort, while others were in the “blind” cohort – only provided MCU current sensors
without the kiosk.