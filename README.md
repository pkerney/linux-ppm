# linux-ppm
Code and utilities to use USB game controllers, HOTAS and joysticks on Linux and use a serial connected Arduino to generated PPM signals to feed to radio control systems like Ardupilot and iNAV

No support for telemtry return.

- js_list.py : Utility to list all the Joystick devices as well as axes and buttons per device.
- ppm-1.ino : Arduino sketch to accept serial commands to set channel outputs
- js_arduino.py : Main Python app that read a config file and then listens for the joystick events and sends values to the Arduino
- config.json : Example config file
- mavlink.py : (not really related, but anyway) Print mavlink messages coming from serial port

Disclaimer: Not tested on a live vehicle. MissionPlanner can see the PPM values which indicates that the Arduino can behave like a TX
Disclaimer 2: I'm not the world's neatest programmer and definitely not an expert in Python.

TODO: See if this can work with a trainer port (PPM input) or something like a TX module that takes a PPM input.
TODO 2: Dig up attributions for other stolen code. (I'm sure you know how it is, just find something, cut/paste, lose original link)

Usage:

- Load ppm-1.ino onto an Arduino. I used an Uno. Only need signal and ground to go to the module or TX.
- Run js_list.py and work out the names of the controllers and the axes/buttons.
- Build config.json.
- Run js_arduino.py and life should be good. You should see the buttons/axes echoed back from the Arduino in the python output.
