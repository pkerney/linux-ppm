# linux-ppm
Code and utilities to use USB game controllers and joysticks on Linux connected and use a serial connected Arduino to generated PPM signals to feed to radio control systems like Ardupilot and iNAV

Code coming

- js_list.py : Utility to list all the Joystick devices as well as axes and buttons per device.
- ppm-1.ino : Arduino sketch to accept serial commands to set channel outputs
- js_arduino.py : Main Python app that read a config file and then listens for the joystick events and sends values to the Arduino
- config.json : Example config file
- mavlink.py : (not really related, but anyway) Print mavlink messages coming from serial port
- 
