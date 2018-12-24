#!/usr/bin/env python

import os
import sys

import configargparse


def get_args():
    default_config = []

    if '-cf' not in sys.argv and '--config' not in sys.argv:
        default_config = [os.getenv('VISION_CONFIG', os.path.join(os.path.dirname(__file__), '../config/config.ini'))]

    parser = configargparse.ArgParser(default_config_files=default_config, auto_env_var_prefix='VISION_')

    parser.add_argument("-i", "--image", help="path to image")
    parser.add_argument("-s", "--source", type=int, default=0, help="video source (default=0)")
    parser.add_argument("-d", "--display", action="store_true", help="display results of processing in a new window")
    parser.add_argument("-t", "--team", type=int, help="the team of the target roboRIO")
    parser.add_argument("-na", "--min-area", type=int, help="minimum area for blobs")
    parser.add_argument("-xa", "--max-area", type=int, help="maximum area for blobs")
    parser.add_argument("-nf", "--min-full", type=float, help="minimum fullness of blobs")
    parser.add_argument("-xf", "--max-full", type=float, help="maximum fullness of blobs")
    parser.add_argument("-hf", "--horizontal-fov", type=float, help="horizontal fov of camera")
    parser.add_argument("-vf", "--vertical-fov", type=float, help="vertical fov of camera")
    parser.add_argument("-tw", "--target-width", type=float, help="width 1m away")
    parser.add_argument("-th", "--target-height", type=float, help="height 1m away")
    parser.add_argument("-l", "--lower-color", action="append", nargs="+", type=int, help="lower color threshold in HSV")
    parser.add_argument("-u", "--upper-color", action="append", nargs="+", type=int, help="upper color threshold in HSV")
    parser.add_argument("-tn", "--tuning", action="store_true", help="open in tuning mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="for debugging, prints useful values")

    return vars(parser.parse_args())
