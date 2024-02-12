"""
Example of how to filter for specific mavlink messages coming from the
autopilot using pymavlink.

Can also filter within recv_match command - see "Read all parameters" example
"""

messages = [
    'HEARTBEAT',
    'SYS_STATUS',
#    'GPS_RAW_INT',
    'JUNK'
]

from datetime import datetime

import signal
import sys

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

# Import mavutil
from pymavlink import mavutil

from argparse import ArgumentParser
parser = ArgumentParser(description=__doc__)
parser.add_argument("--source-system", dest='SOURCE_SYSTEM', type=int, default=255, help='MAVLink source system for this GCS')
parser.add_argument("-a", "--all", help="display message type for all messages", action='store_true')

parser.add_argument("-b", "--baudrate", type=int, help="master port baud rate", default=14400)
parser.add_argument("-D", "--device", help="serial device", default="/dev/ttyS0")

args = parser.parse_args()

# Create the connection
# From topside computer

print("port=", args.device, " baud=", args.baudrate, sep='')
master = mavutil.mavlink_connection(args.device, baud=args.baudrate, source_system=args.SOURCE_SYSTEM)

signal.signal(signal.SIGINT, signal_handler)

while True:
    msg = master.recv_match()
    if not msg:
        continue
    now = datetime.now()
    time = now.strftime("%H:%M:%S")
    if args.all :
        print(time, " : ", msg.get_type())

    if msg.get_type() in messages :
        print(time, " : ", msg)
        # print("\nAs dictionary: %s" % msg.to_dict())
        # Armed = MAV_STATE_STANDBY (4), Disarmed = MAV_STATE_ACTIVE (3)
        # print("\nSystem status: %s" % msg.system_status)
