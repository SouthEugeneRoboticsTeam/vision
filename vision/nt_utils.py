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
    try:
        if vision_table:
            vision_table.putNumber(key, value)
        elif verbose:
            print("[NetworkTable] not connected")
    except:
        print("NetworkTable error putting number")


def put_boolean(key, value):
    try:
        if vision_table:
            vision_table.putBoolean(key, value)
        elif verbose:
            print("[NetworkTable] not connected")
    except:
        print("NetworkTable error putting boolean")


def get_boolean(key):
    try:
        if vision_table:
            return vision_table.getBoolean(key)
        elif verbose:
            print("[NetworkTable] not connected")
    except:
        return False
        print("NetworkTable error getting boolean")


def get_number(key):
    try:
        if vision_table:
            return vision_table.getNumber(key)
        elif verbose:
            print("[NetworkTable] not connected")
    except:
        return 0
        print("NetworkTable error getting number")
