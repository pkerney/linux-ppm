# linux-ppm
Code and utilities to use USB game controllers, HOTAS and joysticks on Linux and use a serial connected Arduino to generated PPM signals to feed to radio control systems like Ardupilot and iNAV

- js_list.py : Utility to list all the Joystick devices as well as axes and buttons per device.
- ppm-1.ino : Arduino sketch to accept serial commands to set channel outputs
- js_arduino.py : Main Python app that read a config file and then listens for the joystick events and sends values to the Arduino
- config.json : Example config file
- mavlink.py : (not really related, but anyway) Print mavlink messages coming from serial port

Disclaimer: Not tested on a live vehicle. MissionPlanner can see the PPM values which indicates that the Arduino can behave like a TX

TODO: See if this can work with a trainer port (PPM input) or something like a TX module that takes a PPM input.

No support for telemtry return.

Usage:

- Load ppm-1.ino onto an Arduino. I used an Uno.
- Run js_list.py and work out the names of the controllers and the axes/buttons.
- Build config.json.
- Run js_arduino.py and life should be good.
