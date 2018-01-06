#!/usr/bin/env python

import configargparse
import os
import sys


def get_args():
    default_config = []

    if '-cf' not in sys.argv and '--config' not in sys.argv:
        default_config = [os.getenv('VISION_CONFIG', os.path.join(os.path.dirname(__file__), '../config/config.ini'))]

    parser = configargparse.ArgParser(default_config_files=default_config, auto_env_var_prefix='VISION_')

    parser.add_argument("-i", "--image", help="path to image")
    parser.add_argument("-s", "--source", type=int, default=0, help="video source (default=0)")
    parser.add_argument("-d", "--display", action="store_true", help="display results of processing in a new window")
    parser.add_argument("-ip", "--roborio-ip", help="the ip address of the roboRIO")
    parser.add_argument("-ma", "--min-area", type=int, help="minimum area for blobs")
    parser.add_argument("-mx", "--max-area", type=int, help="maximum area for blobs")
    parser.add_argument("-lt", "--lower-color", action="append", nargs="+", type=int, help="lower color threshold for BGR values")
    parser.add_argument("-ut", "--upper-color", action="append", nargs="+", type=int, help="upper color threshold for BGR values")
    parser.add_argument("-v", "--verbose", action="store_true", help="for debugging, prints useful values")

    return vars(parser.parse_args())
