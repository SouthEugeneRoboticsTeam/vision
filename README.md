# SERT Vision

[![Team 2521][team-img]][team-url]
[![Python 2.7][python-img]][python-url]
[![License][license-img]][license-url]
[![Travis][travis-img]][travis-url]

SERT's OpenCV vision code.

## Usage

Before starting the program, you must install OpenCV v2.4.x along with the
pip dependencies:

```bash
$ pip install -r requirements.txt
```

Then, you can run the program using:

```bash
$ python run.py
```

## Configuration

All command-line arguments may be configured in the `config.ini` file
(located at `config/config.ini`). For example, the `--lower-rgb`
argument may be edited using the `lower-rgb` line in the `config.ini`.

```
-h, --help            show this help message and exit
-i IMAGE, --image IMAGE
					  path to image [env var: VISION_IMAGE]
-ma MIN_AREA, --min-area MIN_AREA
					  minimum area for blobs [env var: VISION_MIN_AREA]
-lt LOWER_RGB [LOWER_RGB ...], --lower-rgb LOWER_RGB [LOWER_RGB ...]
					  lower threshold for RGB values [env var: VISION_LOWER_RGB]
-ut UPPER_RGB [UPPER_RGB ...], --upper-rgb UPPER_RGB [UPPER_RGB ...]
					  upper threshold RGB values [env var: VISION_UPPER_RGB]
-d, --display         display results of processing in a new window [env var: VISION_DISPLAY]
-v, --verbose         for debugging, prints useful values [env var: VISION_VERBOSE]
-ip ROBORIO_IP, --roborio-ip ROBORIO_IP
					  the ip address of the roboRIO [env var: VISION_ROBORIO_IP]
```

<!-- Badge URLs -->

[team-img]:     https://img.shields.io/badge/team-2521-7d26cd.svg?style=flat-square
[team-url]:     https://sert2521.org
[python-img]:   https://img.shields.io/badge/python-2.7-blue.svg?style=flat-square
[python-url]:   https://www.python.org/downloads
[license-img]:  https://img.shields.io/github/license/andrewda/robotics-vision.svg?style=flat-square
[license-url]:  https://github.com/andrewda/robotics-vision/blob/master/LICENSE
[travis-img]:   https://img.shields.io/travis/andrewda/robotics-vision.svg?style=flat-square
[travis-url]:   https://travis-ci.org/andrewda/robotics-vision
