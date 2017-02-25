#!/usr/bin/env python

import logging
from networktables import NetworkTables
from . import args

ip = args["roborio_ip"]
verbose = args["verbose"]

vision_table = False

if verbose:
	logging.basicConfig(level=logging.DEBUG)
else:
	logging.basicConfig(level=logging.INFO)

if ip is not None:
	NetworkTables.initialize(server=ip)

	vision_table = NetworkTables.getTable("Vision")


def put_number(key, value):
#	print key, value
	if vision_table:
		vision_table.putNumber(key, value)
	elif verbose:
		print("[NetworkTable] not connected")

def put_boolean(key, value):
	print key, value
	if vision_table:
		vision_table.putBoolean(key, value)
	elif verbose:
		print("[NetworkTable] not connected")

def get_boolean(key):
	if vision_table:
		print vision_table.getBoolean(key)
		return vision_table.getBoolean(key)
	elif verbose:
		print("[NetworkTable] not connected")

def get_number(key):
        if vision_table:
                print vision_table.getNumber(key)
                return vision_table.getNumber(key)
        elif verbose:
                print("[NetworkTable] not connected")


#put_boolean("front_camera", True)
#put_number("front_lower_blue", 0)
#put_number("front_lower_green", 0)
#put_number("front_lower_red", 0)
#put_number("front_upper_blue", 0)
#put_number("front_upper_green", 0)
#put_number("front_upper_red", 0)
#put_number("rear_lower_blue", 0)
#put_number("rear_lower_green", 0)
#put_number("rear_lower_red", 0)
#put_number("rear_upper_blue", 0)
#put_number("rear_upper_green", 0)
#put_number("rear_upper_red", 0)
