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
	if vision_table:
		vision_table.putNumber(key, value)
	elif verbose:
		print("[NetworkTable] not connected")
