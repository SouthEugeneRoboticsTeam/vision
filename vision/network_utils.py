#!/usr/bin/env python

import logging
import time

from networktables import NetworkTablesInstance

from . import args

if args["verbose"]:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

nt = NetworkTablesInstance.getDefault()
nt.startClientTeam(args["team"])

# Uncomment the following line to use a local NetworkTables instance (e.g. OutlineViewer)
# _nt.startClient("127.0.0.1")

table = nt.getTable("Vision")


def put(key, value):
    table.putValue("last_alive", time.time() * 1000)
    table.putValue(key, value)


def get(key, default=None):
    table.putValue("last_alive", time.time() * 1000)
    return table.getValue(key, default)
