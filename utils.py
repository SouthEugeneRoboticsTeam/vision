import sys
import os
import configargparse

def get_args():
	default_config = []

	if '-cf' not in sys.argv and '--config' not in sys.argv:
		default_config = [os.getenv('VISION_CONFIG', os.path.join(os.path.dirname(__file__), '../config/config.ini'))]

	parser = configargparse.ArgParser(default_config_files=default_config, auto_env_var_prefix='VISION_')

	parser.add_argument("-i", "--image", help="Path to image")
	parser.add_argument("-ma", "--minarea", help="Minimum area for blobs")
	parser.add_argument("-lt", "--lowrgb", nargs='+', help="Lower threshold for RGB values")
	parser.add_argument("-ut", "--uprgb", nargs='+', help="Upper threshold RGB values")

	args = vars(parser.parse_args())

	# Define minimum area
	if args["minarea"] is None:
		args["minarea"] = 1000

	# Define lower and upper thresholds (RGB)
	if args["lowrgb"] is None:
		args["lowrgb"] = [0, 20, 0]

	if args["uprgb"] is None:
		args["uprgb"] = [30, 255, 30]

	return args
