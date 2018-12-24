# SERT Vision

[![Team 2521][team-img]][team-url]
[![Python 3.6][python-img]][python-url]
[![License][license-img]][license-url]
[![Travis][travis-img]][travis-url]

SERT's OpenCV vision code.

## Usage

Before starting the program, you must install OpenCV >= v3.1.x along with
the pip dependencies:

```bash
$ pip install -r requirements.txt
```

Then, you can run the program using:

```bash
$ python run.py
```

Full usage:

```text
usage: run.py [-h] [-i IMAGE] [-s SOURCE] [-d] [-ip ROBORIO_IP]
              [-p ROBORIO_PORT] [-ma MIN_AREA] [-mx MAX_AREA]
              [-l LOWER_COLOR [LOWER_COLOR ...]]
              [-u UPPER_COLOR [UPPER_COLOR ...]] [-t] [-v]
```

## Configuration

### Command-Line Options

All command-line arguments may be configured in the `config.ini` file
(located at `config/config.ini`). For example, the `--lower-rgb`
argument may be edited using the `lower-rgb` line in the `config.ini`.

```text
  -h, --help            show this help message and exit
  -i IMAGE, --image IMAGE
                        path to image
  -s SOURCE, --source SOURCE
                        video source (default=0)
  -d, --display         display results of processing in a new window
  -ip ROBORIO_IP, --roborio-ip ROBORIO_IP
                        the ip address of the roboRIO
  -p ROBORIO_PORT, --roborio-port ROBORIO_PORT
                        the port of the roboRIO's UDP server
  -ma MIN_AREA, --min-area MIN_AREA
                        minimum area for blobs
  -mx MAX_AREA, --max-area MAX_AREA
                        maximum area for blobs
  -l LOWER_COLOR [LOWER_COLOR ...], --lower-color LOWER_COLOR [LOWER_COLOR ...]
                        lower color threshold in HSV
  -u UPPER_COLOR [UPPER_COLOR ...], --upper-color UPPER_COLOR [UPPER_COLOR ...]
                        upper color threshold in HSV
  -t, --tuning          open in tuning mode
  -v, --verbose         for debugging, prints useful values
```

### Camera

For use with the Microsoft Lifecam 3000, the camera's exposure should be
set manually because the Lifecam will auto-adjust otherwise, making
thresholding difficult. This can be done with V4L:

```
$ sudo apt-get install v4l-utils
$ v4l-ctl -d /dev/video0 -c exposure_absolute=50
```

<!-- Badge URLs -->

[team-img]:     https://img.shields.io/badge/team-2521-7d26cd.svg?style=flat-square
[team-url]:     https://sert2521.org
[python-img]:   https://img.shields.io/badge/python-3.6-blue.svg?style=flat-square
[python-url]:   https://www.python.org/downloads
[license-img]:  https://img.shields.io/github/license/SouthEugeneRoboticsTeam/vision.svg?style=flat-square
[license-url]:  https://github.com/SouthEugeneRoboticsTeam/vision/blob/master/LICENSE
[travis-img]:   https://img.shields.io/travis/SouthEugeneRoboticsTeam/vision/master.svg?style=flat-square
[travis-url]:   https://travis-ci.org/SouthEugeneRoboticsTeam/vision
