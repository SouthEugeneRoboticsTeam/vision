import sys
import os
import configargparse

def get_args():
	default_config = []

	if '-cf' not in sys.argv and '--config' not in sys.argv:
		default_config = [os.getenv('VISION_CONFIG', os.path.join(os.path.dirname(__file__), 'config/config.ini'))]

	parser = configargparse.ArgParser(default_config_files=default_config, auto_env_var_prefix='VISION_')

	parser.add_argument("-i", "--image", help="Path to image")
	parser.add_argument("-ma", "--min-area", type=int, help="Minimum area for blobs")
	parser.add_argument("-lt", "--lower-rgb", action="append", type=int, help="Lower threshold for RGB values")
	parser.add_argument("-ut", "--upper-rgb", action="append", type=int, help="Upper threshold RGB values")

	return vars(parser.parse_args())
