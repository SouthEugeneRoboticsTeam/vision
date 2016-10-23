#!/usr/bin/env python

from networktables import NetworkTable

from . import args

ip = args["roborio_ip"]
verbose = args["verbose"]

vision_table = False

if ip is not None:
	NetworkTable.setIPAddress(ip)
	NetworkTable.setClientMode()
	NetworkTable.initialize()

	vision_table = NetworkTable.getTable("vision")

def put_number(key, value):
	if vision_table:
		vision_table.putNumber(key, value)
	elif verbose:
		print("[NetworkTable] not connected")
