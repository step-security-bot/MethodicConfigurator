#!/usr/bin/env python

'''
Print flight controller banner statustext messages

SPDX-FileCopyrightText: 2024 Amilcar do Carmo Lucas <amilcar.lucas@iav.de>

SPDX-License-Identifier: GPL-3.0-or-later
'''

import time

from argparse import ArgumentParser

from pymavlink import mavutil


def print_banner_messages(master):
    '''Decode and print banner information from the flight controller'''
    start_time = time.time()
    while True:
        msg = master.recv_match(blocking=False)
        if msg is not None:
            if msg.get_type() == 'STATUSTEXT':
                print(f"{msg.text}")
        if time.time() - start_time > 2:  # Check if 2 seconds have passed since the start of the loop
            break  # Exit the loop if 2 seconds have elapsed

def request_banner(master):
    '''Request banner information from the flight controller'''
    # https://mavlink.io/en/messages/ardupilotmega.html#MAV_CMD_DO_SEND_BANNER
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SEND_BANNER,
        0,
        0,  # param1: 0
        0,  # param2: 0
        0,  # param3: 0
        0,  # param4: 0
        0,  # param5: 0
        0,  # param6: 0
        0   # param7: 0
    )

def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--baudrate", type=int,
                    help="master port baud rate", default=115200)
    parser.add_argument("--device", required=True, help="serial device")
    parser.add_argument("--source-system", dest='SOURCE_SYSTEM', type=int,
                    default=255, help='MAVLink source system for this GCS')
    args = parser.parse_args()

    # Connect to the flight controller
    connection = mavutil.mavlink_connection(args.device, baud=args.baudrate, source_system=args.SOURCE_SYSTEM)

    try:
        connection.wait_heartbeat(timeout=60)  # Wait for heartbeat to confirm connection
        request_banner(connection)
        print_banner_messages(connection)
    except KeyboardInterrupt:
        print("\nDisconnecting...")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
