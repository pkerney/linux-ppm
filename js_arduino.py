import os, struct, array
from fcntl import ioctl, fcntl, F_GETFL, F_SETFL
import json
import serial

VALUE_LOW = 1000
VALUE_HIGH = 2000

BUTTON_OFF = VALUE_LOW
BUTTON_ON = VALUE_HIGH

# These constants were borrowed from linux/input.h
axis_names = {
    0x00 : 'x',
    0x01 : 'y',
    0x02 : 'z',
    0x03 : 'rx',
    0x04 : 'ry',
    0x05 : 'rz',
    0x06 : 'throttle',
    0x07 : 'rudder',
    0x08 : 'wheel',
    0x09 : 'gas',
    0x0a : 'brake',
    0x10 : 'hat0x',
    0x11 : 'hat0y',
    0x12 : 'hat1x',
    0x13 : 'hat1y',
    0x14 : 'hat2x',
    0x15 : 'hat2y',
    0x16 : 'hat3x',
    0x17 : 'hat3y',
    0x18 : 'pressure',
    0x19 : 'distance',
    0x1a : 'tilt_x',
    0x1b : 'tilt_y',
    0x1c : 'tool_width',
    0x20 : 'volume',
    0x28 : 'misc',
}

button_names = {
    0x120 : 'trigger',
    0x121 : 'thumb',
    0x122 : 'thumb2',
    0x123 : 'top',
    0x124 : 'top2',
    0x125 : 'pinkie',
    0x126 : 'base',
    0x127 : 'base2',
    0x128 : 'base3',
    0x129 : 'base4',
    0x12a : 'base5',
    0x12b : 'base6',
    0x12f : 'dead',
    0x130 : 'a',
    0x131 : 'b',
    0x132 : 'c',
    0x133 : 'x',
    0x134 : 'y',
    0x135 : 'z',
    0x136 : 'tl',
    0x137 : 'tr',
    0x138 : 'tl2',
    0x139 : 'tr2',
    0x13a : 'select',
    0x13b : 'start',
    0x13c : 'mode',
    0x13d : 'thumbl',
    0x13e : 'thumbr',

    0x220 : 'dpad_up',
    0x221 : 'dpad_down',
    0x222 : 'dpad_left',
    0x223 : 'dpad_right',

    # XBox 360 controller uses these codes.
    0x2c0 : 'dpad_left',
    0x2c1 : 'dpad_right',
    0x2c2 : 'dpad_up',
    0x2c3 : 'dpad_down',
}


def map_range(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min




def send_to_arduino(channel,value):
    #print('send_to_arduino('+str(channel)+','+str(value)+')')
    ser.write((str(channel)+","+str(value)+'\n').encode())
    ser.flush()




class jsdev:
  def __init__(self, devname):
    self.devname = devname
    self.axis_map = []
    self.button_map = []
    self.fn = '/dev/input/'+self.devname
    self.jsdev = open(self.fn, 'rb', buffering=0)
    fcntl(self.jsdev, F_SETFL, fcntl(self.jsdev, F_GETFL) | os.O_NONBLOCK)

    # Get the device name.
    self.buf = array.array('B', [0] * 64)
    ioctl(self.jsdev, 0x80006a13 + (0x10000 * len(self.buf)), self.buf) # JSIOCGNAME(len)
    self.js_name = self.buf.tobytes().rstrip(b'\x00').decode('utf-8')
    print('')
    print('%s: %s' % (self.fn,self.js_name))

    # Get number of axes and buttons.
    self.buf = array.array('B', [0])
    ioctl(self.jsdev, 0x80016a11, self.buf) # JSIOCGAXES
    self.num_axes = self.buf[0]

    self.buf = array.array('B', [0])
    ioctl(self.jsdev, 0x80016a12, self.buf) # JSIOCGBUTTONS
    self.num_buttons = self.buf[0]

    # Get the axis map.
    self.buf = array.array('B', [0] * 0x40)
    ioctl(self.jsdev, 0x80406a32, self.buf) # JSIOCGAXMAP

    self.axis_map = []
    self.button_map = []
    self.axis_states = {}
    self.button_states = {}

    for self.axis in self.buf[:self.num_axes]:
        self.axis_name = axis_names.get(self.axis, 'unknown(0x%02x)' % self.axis)
        self.axis_map.append(self.axis_name)
        self.axis_states[self.axis_name] = VALUE_LOW + ((VALUE_HIGH-VALUE_LOW)/2)

    # Get the button map.
    self.buf = array.array('H', [0] * 200)
    ioctl(self.jsdev, 0x80406a34, self.buf) # JSIOCGBTNMAP

    for self.btn in self.buf[:self.num_buttons]:
        self.btn_name = button_names.get(self.btn, 'unknown(0x%03x)' % self.btn)
        self.button_map.append(self.btn_name)
        self.button_states[self.btn_name] = BUTTON_OFF

    print('%d axes found: %s' % (self.num_axes, ', '.join(self.axis_map)))
    print('%d buttons found: %s' % (self.num_buttons, ', '.join(self.button_map)))




print('')
print('Channel configuration:')

# Opening JSON file
f = open('config.json')
config = json.load(f)
f.close()

# Iterate through the jsonlist
for i in config['channels']:
    print(i['channel'],i['device'],i['name'])


# open the arduino
print('')
print('Open Arduino:')
print("Arduino on port",config['arduino']['port'],"with speed",config['arduino']['baud'])
ser = serial.Serial(config['arduino']['port'],config['arduino']['baud'],timeout=0.01)




jsdevs = {}

# Iterate over the joystick devices.
print('')
print('Available devices:')

for filename in os.listdir('/dev/input'):
    if filename.startswith('js'):
        jsdevs[filename] = jsdev(filename)


def process_channel(dev, name, value):
    for d in jsdevs:
        if jsdevs[d].fn == dev:
            for i in config['channels']:
                if i["device"] == jsdevs[d].js_name:
                    if i["name"] == name:
                        #print("process_channel()", dev, name, value)
                        send_to_arduino(i['channel'],value)

def reset_values():
    print("Resetting - sending all values")
    for i in config['channels']:
        for d in jsdevs:
            if jsdevs[d].js_name == i['device']:
                value = -1
                try:
                    value = jsdevs[d].axis_states[i['name']]
                except KeyError as e:
                    pass
                except IndexError as e:
                    pass

                try:
                    value = jsdevs[d].button_states[i['name']]
                    if value == 0 or value == BUTTON_OFF:
                        value = BUTTON_OFF
                    else:
                        value = BUTTON_ON
                except KeyError as e:
                    pass
                except IndexError as e:
                    pass

                send_to_arduino(i['channel'],value)




def read_input(dev):
    evbuf = dev.jsdev.read(8)
    if evbuf:
        time, value, type, number = struct.unpack('IhBB', evbuf)

        if type & 0x01:
            button = dev.button_map[number]
            if button:
                if value == 0:
                    dev.button_states[button] = BUTTON_OFF
                    #print("%s: %s released" % (dev.jsdev.name, button))
                else:
                    dev.button_states[button] = BUTTON_ON
                    #print("%s: %s pressed" % (dev.jsdev.name, button))
                process_channel(dev.jsdev.name, button, dev.button_states[button])

        if type & 0x02:
            axis = dev.axis_map[number]
            if axis:
                dev.axis_states[axis] = map_range(value,-32767,32767,VALUE_LOW,VALUE_HIGH)
                #print("%s: %s: %d" % (dev.jsdev.name, axis, dev.axis_states[axis]))
                process_channel(dev.jsdev.name, axis, dev.axis_states[axis])

        if type & 0x80:
            #print("(initial) ",value, type, number)
            pass



print('')
print('Running:')

while True:

    # process all the jotstick devices
    for dev in jsdevs:
        read_input(jsdevs[dev])
    
    # process data from the Arduino
    line = ser.readline()
    line_str=line.decode(errors='ignore')
    line_str=line_str.rstrip()
    if len(line)>0:

        # There is a 5s heartbeat coming from the arduino
        if line_str[0] == 't': # ACK of the message
            print('Arduino->'+line_str+'<-')
        if line_str[0] == 'c': # ACK of the message
            print('Arduino->'+line_str+'<-')
        if (line_str=="reset"):
            reset_values()
            
