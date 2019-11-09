#!/usr/bin/env python

import os
import sys

import configargparse


# Returns a dictionary of arguments that can be adjusted through the command line
def get_args():
    default_config = []

    # Get default config arguments from the config.ini file
    if '-cf' not in sys.argv and '--config' not in sys.argv:
        default_config = [os.getenv('VISION_CONFIG', os.path.join(os.path.dirname(__file__), '../config/config.ini'))]

    parser = configargparse.ArgParser(default_config_files=default_config, auto_env_var_prefix='VISION_')

    parser.add_argument('-i', '--image', help='path to image')
    parser.add_argument('-n', '--name', type=str, default='camera', help='the name of this camera')
    parser.add_argument('-s', '--source', type=str, default='/dev/video0',
                        help='path to video source (default=/dev/video0)')
    parser.add_argument('-c', '--camera', type=str, default='cameras/camera1_16-9.cam',
                        help='path to camera file (default=camera/camera1_4-3.cam)')
    parser.add_argument('-t', '--team', type=int, help='the team of the target roboRIO')
    parser.add_argument('-d', '--display', action='store_true', help='display results of processing in a new window')
    parser.add_argument('-na', '--min-area', type=int, help='minimum area for blobs')
    parser.add_argument('-xa', '--max-area', type=int, help='maximum area for blobs')
    parser.add_argument('-nf', '--min-full', type=float, help='minimum fullness of blobs')
    parser.add_argument('-xf', '--max-full', type=float, help='maximum fullness of blobs')
    parser.add_argument('-l', '--lower-color', action='append', nargs='+',
                        type=int, help='lower color threshold in HSV')
    parser.add_argument('-u', '--upper-color', action='append', nargs='+',
                        type=int, help='upper color threshold in HSV')
    parser.add_argument('-tn', '--tuning', action='store_true', help='open in tuning mode')
    parser.add_argument('-v', '--verbose', action='store_true', help='for debugging, prints useful values')

    return vars(parser.parse_args())
